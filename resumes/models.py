import os
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_resume_file(value):
    """Ensure uploaded resume is only PDF or TXT."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.txt']
    if ext not in valid_extensions:
        raise ValidationError("Only .pdf and .txt files are supported for resume uploads.")


class Resume(models.Model):
    """Resume model storing the uploaded file and extracted text for each student."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume',
        help_text="Each student can have exactly one resume",
    )
    file = models.FileField(
        upload_to='resumes/',
        validators=[validate_resume_file],
    )
    # Extracted raw text from resume for AI matching
    extracted_text = models.TextField(
        blank=True,
        default='',
        help_text="Extracted text from the uploaded resume file",
    )
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume - {self.user.username}"
