from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobForm
from accounts.decorators import admin_required


from resumes.models import Resume
from resumes.matcher import match


@login_required
def job_list_view(request):
    """
    List all jobs with basic search by title, required skills, or company.
    For students, computes and displays their personal resume match score next to each job.
    """
    query = request.GET.get('q', '').strip()
    jobs = list(Job.objects.all().order_by('-created_at'))

    # Basic search filter
    if query:
        jobs = [
            j for j in jobs
            if query.lower() in j.title.lower()
            or query.lower() in j.company.lower()
            or query.lower() in j.required_skills.lower()
        ]

    # Check student's resume & calculate match scores
    applied_job_ids = set()
    student_resume = None
    has_resume = False

    if request.user.role == 'student':
        applied_job_ids = set(
            Application.objects.filter(user=request.user).values_list('job_id', flat=True)
        )
        student_resume = Resume.objects.filter(user=request.user).first()
        if student_resume and student_resume.extracted_text:
            has_resume = True
            for job in jobs:
                res = match(student_resume.extracted_text, job.required_skills)
                job.match_score = res['score']
        else:
            for job in jobs:
                job.match_score = None
    else:
        for job in jobs:
            job.match_score = None

    context = {
        'jobs': jobs,
        'query': query,
        'total_jobs_count': len(jobs),
        'applied_job_ids': applied_job_ids,
        'has_resume': has_resume,
        'is_admin': request.user.role == 'admin' or request.user.is_superuser,
    }
    return render(request, 'jobs/job_list.html', context)


@login_required
def job_detail_view(request, job_id):
    """
    View complete job details, description, company, required skill tags,
    and student's resume match score breakdown.
    """
    job = get_object_or_404(Job, id=job_id)
    is_admin = request.user.role == 'admin' or request.user.is_superuser

    user_application = None
    student_match = None
    if request.user.role == 'student':
        user_application = Application.objects.filter(user=request.user, job=job).first()
        student_resume = Resume.objects.filter(user=request.user).first()
        if student_resume and student_resume.extracted_text:
            student_match = match(student_resume.extracted_text, job.required_skills)

    context = {
        'job': job,
        'skills': job.get_skills_list(),
        'is_admin': is_admin,
        'user_application': user_application,
        'student_match': student_match,
    }
    return render(request, 'jobs/job_detail.html', context)



@admin_required
def job_create_view(request):
    """
    Allow placement admins to post a new job opening.
    Protected by @admin_required decorator.
    """
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job posting '{job.title}' at '{job.company}' created successfully!")
            return redirect('jobs:detail', job_id=job.id)
        else:
            messages.error(request, "Please fix the errors below to create the job posting.")
    else:
        form = JobForm()

    return render(request, 'jobs/job_form.html', {'form': form, 'action_title': 'Post New Job'})


@admin_required
def job_edit_view(request, job_id):
    """
    Allow placement admins to update an existing job posting.
    Protected by @admin_required decorator.
    """
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job posting '{job.title}' updated successfully!")
            return redirect('jobs:detail', job_id=job.id)
        else:
            messages.error(request, "Please fix the errors below to update the job posting.")
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'action_title': f'Edit Job: {job.title}',
    })


@admin_required
def job_delete_view(request, job_id):
    """
    Allow placement admins to delete a job posting with confirmation.
    Protected by @admin_required decorator.
    """
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        title = job.title
        company = job.company
        job.delete()
        messages.info(request, f"Job posting '{title}' at '{company}' has been deleted.")
        return redirect('jobs:list')

    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


# ==========================================
# Applications & Status Tracking Features
# ==========================================

from django.http import JsonResponse
import json
from accounts.decorators import student_required


@student_required
def apply_job_view(request, job_id):
    """
    Allows a student to apply for a job with one click.
    Calculates and persists candidate's current AI match score at time of application.
    """
    job = get_object_or_404(Job, id=job_id)
    student = request.user

    # Check if student already applied
    existing_app = Application.objects.filter(user=student, job=job).first()
    if existing_app:
        messages.info(request, f"You have already applied for '{job.title}'. Current status: {existing_app.status}.")
        return redirect('jobs:my_applications')

    # Calculate match score from student resume
    score = 0.0
    resume = Resume.objects.filter(user=student).first()
    if resume and resume.extracted_text:
        match_result = match(resume.extracted_text, job.required_skills)
        score = match_result['score']

    # Create application record
    Application.objects.create(
        user=student,
        job=job,
        status='Applied',
        match_score=score,
    )
    messages.success(request, f"Successfully applied for '{job.title}' at '{job.company}'! (Match score: {score}%)")
    return redirect('jobs:my_applications')


@student_required
def my_applications_view(request):
    """
    'My applications' view for students:
    Displays all submitted applications with a visual multi-step status tracker:
    Applied -> Shortlisted -> Interview -> Selected.
    """
    student = request.user
    applications = Application.objects.filter(user=student).select_related('job').order_by('-applied_at')

    context = {
        'applications': applications,
        'total_count': applications.count(),
        'shortlisted_count': applications.filter(status='Shortlisted').count(),
        'interview_count': applications.filter(status='Interview').count(),
        'selected_count': applications.filter(status='Selected').count(),
    }
    return render(request, 'jobs/my_applications.html', context)


@admin_required
def admin_applicants_view(request):
    """
    'Applicants' page for Admins:
    - Pick a job from a dropdown.
    - View candidates ranked by match score (highest to lowest).
    - Inline status change dropdown powered by asynchronous JavaScript fetch.
    """
    jobs = Job.objects.all().order_by('title')
    selected_job_id = request.GET.get('job_id')
    selected_job = None

    if selected_job_id and selected_job_id.isdigit():
        selected_job = Job.objects.filter(id=int(selected_job_id)).first()
    elif jobs.exists():
        # Default to first job if none specified
        selected_job = jobs.first()

    # Query applicants ranked by match_score descending
    if selected_job:
        applicants = Application.objects.filter(job=selected_job).select_related('user').order_by('-match_score', '-applied_at')
    else:
        applicants = Application.objects.none()

    # Pre-fetch resumes for applicants to display link/status
    applicant_user_ids = [app.user_id for app in applicants]
    resumes_by_user = {
        res.user_id: res for res in Resume.objects.filter(user_id__in=applicant_user_ids)
    }

    # Attach resume to application objects
    for app in applicants:
        app.user_resume = resumes_by_user.get(app.user_id)

    status_choices = Application.STATUS_CHOICES

    context = {
        'jobs': jobs,
        'selected_job': selected_job,
        'applicants': applicants,
        'status_choices': status_choices,
        'total_applicants': applicants.count(),
    }
    return render(request, 'jobs/admin_applicants.html', context)


@admin_required
def update_application_status_api(request, application_id):
    """
    API endpoint for asynchronous status updates via JavaScript fetch().
    Updates status and returns JSON without page reload.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    application = get_object_or_404(Application, id=application_id)

    # Read status from JSON payload or POST body
    new_status = None
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
    except Exception:
        new_status = request.POST.get('status')

    # Validate choice
    valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({
            'success': False,
            'error': f"Invalid status '{new_status}'. Allowed: {valid_statuses}"
        }, status=400)

    # Save update
    application.status = new_status
    application.save(update_fields=['status'])

    return JsonResponse({
        'success': True,
        'application_id': application.id,
        'new_status': application.status,
        'message': f"Application status updated to '{application.status}'"
    })

