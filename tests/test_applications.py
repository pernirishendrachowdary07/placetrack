import json
import pytest
from django.db import IntegrityError
from django.urls import reverse
from accounts.models import User
from jobs.models import Job, Application


@pytest.mark.django_db
class TestDuplicateApplicationPrevention:
    """
    Test suite verifying that a student cannot apply twice to the same job opening.
    Validates enforcement at both database constraint level, Django web view level,
    and REST API level.
    """

    @pytest.fixture
    def student(self):
        return User.objects.create_user(
            username="applicant_student",
            password="TestPassword123!",
            role="student"
        )

    @pytest.fixture
    def job(self):
        return Job.objects.create(
            title="Backend Engineer",
            company="Stripe",
            description="Build payments infrastructure",
            required_skills="Python, Django, SQL"
        )

    # 1. Database level constraint enforcement
    def test_database_unique_constraint_rejects_duplicate(self, student, job):
        """Database UniqueConstraint must raise IntegrityError on duplicate insert."""
        from django.db import transaction

        Application.objects.create(user=student, job=job, status="Applied")

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Application.objects.create(user=student, job=job, status="Applied")

        assert Application.objects.filter(user=student, job=job).count() == 1


    # 2. Web View level duplicate prevention
    def test_web_apply_view_prevents_duplicate_application(self, client, student, job):
        """Applying a second time through the web interface redirects gracefully without duplicating."""
        client.force_login(student)

        # First application
        first_res = client.post(reverse('jobs:apply', kwargs={'job_id': job.id}))
        assert first_res.status_code == 302
        assert Application.objects.filter(user=student, job=job).count() == 1

        # Second application attempt
        second_res = client.post(reverse('jobs:apply', kwargs={'job_id': job.id}))
        assert second_res.status_code == 302

        # Verify application count is still exactly 1
        assert Application.objects.filter(user=student, job=job).count() == 1

    # 3. REST API level duplicate prevention
    def test_api_endpoint_rejects_duplicate_application(self, client, student, job):
        """Calling the DRF application endpoint twice returns 400 Bad Request on second call."""
        client.force_login(student)

        # First API apply call
        res_1 = client.post(
            '/api/applications/',
            data=json.dumps({'job_id': job.id}),
            content_type='application/json'
        )
        assert res_1.status_code == 201

        # Second API apply call for the same job
        res_2 = client.post(
            '/api/applications/',
            data=json.dumps({'job_id': job.id}),
            content_type='application/json'
        )
        assert res_2.status_code == 400
        assert "already applied" in res_2.json()["error"]

        # Ensure only 1 record exists in DB
        assert Application.objects.filter(user=student, job=job).count() == 1
