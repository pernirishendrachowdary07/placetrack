from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def student_required(view_func):
    """
    Decorator to restrict view access to students only.
    - If user is not logged in: redirect to login page.
    - If user is an admin: block access, display message, redirect to admin overview.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to access this page.")
            return redirect('accounts:login')

        if request.user.role != 'student':
            messages.error(request, "Access restricted: This section is for students only.")
            return redirect('accounts:admin_overview')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator to restrict view access to administrators only.
    - If user is not logged in: redirect to login page.
    - If user is a student: block access, display message, redirect to student dashboard.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to access this page.")
            return redirect('accounts:login')

        if request.user.role != 'admin' and not request.user.is_superuser:
            messages.error(request, "Access restricted: Admin privileges required.")
            return redirect('accounts:student_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view
