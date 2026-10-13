from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import student_required
from jobs.models import Job, Application
from .models import Resume
from .forms import ResumeUploadForm
from .matcher import extract_text, match


@student_required
def resume_match_view(request):
    """
    Resume Match Page:
    - Upload PDF or TXT resume (max 5 MB).
    - Extracts readable text. Rejects image/scanned PDFs with clear error.
    - Job dropdown to run matching: displays score %, progress bar, matched and missing skills.
    """
    student = request.user
    resume = Resume.objects.filter(user=student).first()
    jobs = Job.objects.all().order_by('title')

    upload_form = ResumeUploadForm(instance=resume)
    match_result = None
    selected_job_id = None
    selected_job = None

    # 1. Handle File Upload
    if request.method == 'POST' and 'upload_resume' in request.POST:
        upload_form = ResumeUploadForm(request.POST, request.FILES, instance=resume)
        if upload_form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Call extract_text() on the uploaded file
            parsed_text = extract_text(uploaded_file)

            # Check if readable text was found
            if not parsed_text or len(parsed_text.strip()) == 0:
                messages.error(
                    request,
                    "No readable text could be found in your file. "
                    "If you uploaded a scanned PDF or image, please upload a text-based PDF or TXT document."
                )
            else:
                # Save or update Resume instance
                resume_instance = upload_form.save(commit=False)
                resume_instance.user = student
                resume_instance.extracted_text = parsed_text
                resume_instance.save()
                messages.success(request, "Resume uploaded and text extracted successfully! Select a job below to check your match.")
                return redirect('resumes:match')
        else:
            messages.error(request, "Upload failed. Please check the requirements below.")

    # 2. Handle Job Match Request (via GET or POST)
    selected_job_id = request.GET.get('job_id') or request.POST.get('job_id')
    if selected_job_id and selected_job_id.isdigit():
        selected_job = Job.objects.filter(id=int(selected_job_id)).first()
        if selected_job:
            if not resume or not resume.extracted_text:
                messages.warning(request, "Please upload your resume first to calculate job match scores.")
            else:
                # Call matcher
                match_result = match(resume.extracted_text, selected_job.required_skills)

    # Check if student already applied for selected job
    user_application = None
    if selected_job:
        user_application = Application.objects.filter(user=student, job=selected_job).first()

    context = {
        'upload_form': upload_form,
        'resume': resume,
        'jobs': jobs,
        'selected_job': selected_job,
        'selected_job_id': int(selected_job_id) if selected_job_id and selected_job_id.isdigit() else None,
        'match_result': match_result,
        'user_application': user_application,
    }
    return render(request, 'resumes/resume_match.html', context)


@student_required
def apply_to_job_view(request, job_id):
    """
    Apply to a job directly after reviewing match score.
    Automatically records candidate's current AI match score.
    """
    job = get_object_or_404(Job, id=job_id)
    student = request.user

    # Verify if student has a resume
    resume = Resume.objects.filter(user=student).first()
    if not resume or not resume.extracted_text:
        messages.error(request, "You must upload a resume before submitting job applications.")
        return redirect('resumes:match')

    # Calculate current match score
    match_data = match(resume.extracted_text, job.required_skills)
    current_score = match_data['score']

    # Get or create application (enforcing one application per job)
    app, created = Application.objects.get_or_create(
        user=student,
        job=job,
        defaults={
            'status': 'Applied',
            'match_score': current_score,
        }
    )

    if created:
        messages.success(request, f"Successfully applied for '{job.title}' at '{job.company}'! (Match score: {current_score}%)")
    else:
        messages.info(request, f"You have already applied for '{job.title}'. Current status: {app.status}")

    return redirect('jobs:detail', job_id=job.id)
