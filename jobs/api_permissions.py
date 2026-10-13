from rest_framework import permissions


class IsPlacementAdmin(permissions.BasePermission):
    """
    Allows access only to placement admin users (or superusers).
    """
    message = "Admin privileges required to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'admin' or request.user.is_superuser)
        )


class IsStudentUser(permissions.BasePermission):
    """
    Allows access only to student users.
    """
    message = "Student account required to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows authenticated users to read (GET, HEAD, OPTIONS).
    Restricts write operations (POST, PUT, PATCH, DELETE) to admins.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Read permissions are allowed to any authenticated user (students & admins)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write operations require admin role
        return request.user.role == 'admin' or request.user.is_superuser
