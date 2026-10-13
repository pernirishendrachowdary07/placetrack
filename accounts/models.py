from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Role choices: distinguish students from placement admins
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text="Role determining user permissions (student or admin)",
    )

    def is_student(self):
        return self.role == 'student'

    def is_placement_admin(self):
        return self.role == 'admin' or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
