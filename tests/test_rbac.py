import pytest
from django.urls import reverse
from accounts.models import User
from jobs.models import Job


@pytest.mark.django_db
class TestRoleBasedAccessControl:
    """
    Test suite verifying that role-based permissions strictly protect admin routes
    and prevent students from accessing administrative pages.
    """

    @pytest.fixture
    def student(self):
        return User.objects.create_user(
            username="student_user",
            password="TestPassword123!",
            role="student"
        )

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_user(
            username="admin_user",
            password="TestPassword123!",
            role="admin",
            is_staff=True
        )

    @pytest.fixture
    def sample_job(self):
        return Job.objects.create(
            title="Django Engineer",
            company="TestTech",
            description="Build features",
            required_skills="Python, Django"
        )

    # 1. Student blocked from Admin Overview
    def test_student_blocked_from_admin_overview(self, client, student):
        client.force_login(student)
        response = client.get(reverse('accounts:admin_overview'))
        
        # Must be redirected away from admin page to student dashboard
        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')

    # 2. Student blocked from Admin Applicants list
    def test_student_blocked_from_admin_applicants(self, client, student):
        client.force_login(student)
        response = client.get(reverse('jobs:admin_applicants'))

        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')

    # 3. Student blocked from Posting New Job
    def test_student_blocked_from_job_create(self, client, student):
        client.force_login(student)
        response = client.get(reverse('jobs:create'))

        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')

    # 4. Student blocked from Editing Job
    def test_student_blocked_from_job_edit(self, client, student, sample_job):
        client.force_login(student)
        response = client.get(reverse('jobs:edit', kwargs={'job_id': sample_job.id}))

        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')

    # 5. Student blocked from Deleting Job
    def test_student_blocked_from_job_delete(self, client, student, sample_job):
        client.force_login(student)
        response = client.post(reverse('jobs:delete', kwargs={'job_id': sample_job.id}))

        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')
        # Job must NOT have been deleted
        assert Job.objects.filter(id=sample_job.id).exists()

    # 6. Admin can open Admin pages
    def test_admin_access_allowed_on_admin_pages(self, client, admin_user):
        client.force_login(admin_user)

        overview_res = client.get(reverse('accounts:admin_overview'))
        assert overview_res.status_code == 200

        applicants_res = client.get(reverse('jobs:admin_applicants'))
        assert applicants_res.status_code == 200

    # 7. Admin blocked from Student dashboard
    def test_admin_blocked_from_student_dashboard(self, client, admin_user):
        client.force_login(admin_user)
        response = client.get(reverse('accounts:student_dashboard'))

        assert response.status_code == 302
        assert response.url == reverse('accounts:admin_overview')
