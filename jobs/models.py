from django.conf import settings
from django.db import models


class Job(models.Model):
    """Job listing posted by company or placement cell."""
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField()
    # Comma-separated list of required skills (e.g., Python, Django, SQL)
    required_skills = models.TextField(
        help_text="Comma-separated list of required skills (e.g. Python, Django, SQL)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_skills_list(self):
        """Returns clean list of stripped skill tags for badge rendering."""
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def __str__(self):
        return f"{self.title} at {self.company}"



class Application(models.Model):
    """Student application for a specific job."""
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Applied',
    )
    # Match score calculated by AI matching (0.0 to 100.0)
    match_score = models.FloatField(
        default=0.0,
        help_text="AI resume match score percentage",
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A student can apply to a specific job only once
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'job'],
                name='unique_student_job_application',
            )
        ]
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.user.username} - {self.job.title} ({self.status})"
