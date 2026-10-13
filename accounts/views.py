from urllib.parse import urlparse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import StudentRegisterForm, UserLoginForm
from .decorators import student_required, admin_required
from jobs.models import Job, Application
from resumes.models import Resume


def is_url_allowed_for_role(url_path, role, is_superuser=False):
    """
    Check if a path is permitted for the given role to prevent role privilege leakage via 'next'.
    """
    admin_only_prefixes = [
        '/accounts/admin-overview/',
        '/jobs/applicants/',
        '/jobs/create/',
        '/jobs/edit/',
        '/jobs/delete/',
        '/admin/',
    ]
    student_only_prefixes = [
        '/accounts/student-dashboard/',
        '/resumes/match/',
        '/jobs/my-applications/',
        '/jobs/apply/',
    ]
    if role == 'student':
        for prefix in admin_only_prefixes:
            if url_path.startswith(prefix):
                return False
        return True
    elif role == 'admin' or is_superuser:
        for prefix in student_only_prefixes:
            if url_path.startswith(prefix):
                return False
        return True
    return False


def register_view(request):
    """
    Handle self-registration for students.
    Only students can self-register; admins are created by superusers.
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to respective dashboard
        if request.user.role == 'admin' or request.user.is_superuser:
            return redirect('accounts:admin_overview')
        return redirect('accounts:student_dashboard')

    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully for {user.username}! Please log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = StudentRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Dual-card login view displaying Student and Admin login side by side.
    - If already logged in: redirects to user's dashboard.
    - Role verified BEFORE calling login(): wrong-role accounts never receive a session.
    - Errors scoped strictly to the submitted card; submitted username retained.
    - 'next' parameter validated with url_has_allowed_host_and_scheme() and role access.
    """
    if request.user.is_authenticated:
        if request.user.role == 'admin' or request.user.is_superuser:
            return redirect('accounts:admin_overview')
        return redirect('accounts:student_dashboard')

    student_error = None
    admin_error = None
    student_username = ''
    admin_username = ''
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        login_type = request.POST.get('login_type', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '').strip()

        if login_type == 'student':
            student_username = username
        elif login_type == 'admin':
            admin_username = username

        # 1. Authenticate credentials
        user = authenticate(request, username=username, password=password)

        if user is None:
            # Generic error message so usernames are not enumerated
            if login_type == 'admin':
                admin_error = "Invalid username or password"
            else:
                student_error = "Invalid username or password"
        else:
            # 2. Check role BEFORE calling login()
            if login_type == 'student':
                if user.role != 'student':
                    student_error = "This account is not a student account. Use the Admin login."
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        parsed_path = urlparse(next_url).path
                        if is_url_allowed_for_role(parsed_path, user.role, user.is_superuser):
                            return redirect(next_url)
                    return redirect('accounts:student_dashboard')

            elif login_type == 'admin':
                if user.role != 'admin' and not user.is_superuser:
                    admin_error = "This account is not an admin account. Use the Student login."
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        parsed_path = urlparse(next_url).path
                        if is_url_allowed_for_role(parsed_path, user.role, user.is_superuser):
                            return redirect(next_url)
                    return redirect('accounts:admin_overview')

    context = {
        'student_error': student_error,
        'admin_error': admin_error,
        'student_username': student_username,
        'admin_username': admin_username,
        'next': next_url,
    }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    """
    Handle user logout and redirect to login page.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


@student_required
def student_dashboard_view(request):
    """
    Student dashboard: displays student's resume status and job applications.
    Blocked for admin users by @student_required.
    """
    # Fetch student's uploaded resume if exists
    resume = Resume.objects.filter(user=request.user).first()
    # Fetch student's submitted applications
    applications = Application.objects.filter(user=request.user).select_related('job')

    context = {
        'resume': resume,
        'applications': applications,
        'total_applied': applications.count(),
        'shortlisted_count': applications.filter(status='Shortlisted').count(),
    }
    return render(request, 'accounts/student_dashboard.html', context)


from collections import Counter
from django.http import JsonResponse
from django.db.models import Count
from resumes.matcher import match


@admin_required
def admin_overview_view(request):
    """
    Placement Admin overview:
    Displays four key stat cards and interactive Chart.js analytics:
    1. Open jobs
    2. Applications
    3. Shortlisted or beyond
    4. Selected
    """
    open_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    shortlisted_or_beyond = Application.objects.filter(
        status__in=['Shortlisted', 'Interview', 'Selected']
    ).count()
    selected = Application.objects.filter(status='Selected').count()

    recent_applications = Application.objects.select_related('user', 'job').order_by('-applied_at')[:6]

    context = {
        'open_jobs': open_jobs,
        'total_applications': total_applications,
        'shortlisted_or_beyond': shortlisted_or_beyond,
        'selected': selected,
        'recent_applications': recent_applications,
    }
    return render(request, 'accounts/admin_overview.html', context)


@admin_required
def admin_analytics_api(request):
    """
    JSON endpoint for Chart.js analytics on the Admin Overview page:
    1. Four stats: open_jobs, total_applications, shortlisted_or_beyond, selected
    2. Applications per company (bar chart)
    3. Most common missing skills across all applicants (skill gap analysis)
    """
    # 1. Four stat values
    open_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    shortlisted_or_beyond = Application.objects.filter(
        status__in=['Shortlisted', 'Interview', 'Selected']
    ).count()
    selected = Application.objects.filter(status='Selected').count()

    # 2. Applications per company (Bar chart)
    company_data = (
        Job.objects.values('company')
        .annotate(app_count=Count('applications'))
        .order_by('-app_count')
    )
    company_labels = [c['company'] for c in company_data]
    company_counts = [c['app_count'] for c in company_data]

    # 3. Most common missing skills across all applicants
    applications = Application.objects.select_related('job').all()
    applicant_user_ids = [app.user_id for app in applications]
    resumes_by_user = {
        res.user_id: res for res in Resume.objects.filter(user_id__in=applicant_user_ids)
    }

    missing_counter = Counter()
    for app in applications:
        res = resumes_by_user.get(app.user_id)
        if res and res.extracted_text and app.job.required_skills:
            match_data = match(res.extracted_text, app.job.required_skills)
            for skill in match_data.get('missing_skills', []):
                missing_counter[skill] += 1

    # Take top 8 most common missing skills
    top_missing = missing_counter.most_common(8)
    skill_labels = [item[0] for item in top_missing]
    skill_counts = [item[1] for item in top_missing]

    return JsonResponse({
        'stats': {
            'open_jobs': open_jobs,
            'total_applications': total_applications,
            'shortlisted_or_beyond': shortlisted_or_beyond,
            'selected': selected,
        },
        'company_chart': {
            'labels': company_labels,
            'data': company_counts,
        },
        'skills_chart': {
            'labels': skill_labels,
            'data': skill_counts,
        }
    })

