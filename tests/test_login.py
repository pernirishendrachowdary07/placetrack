import pytest
from django.urls import reverse
from accounts.models import User


def get_card_contents(html: str):
    """
    Split the HTML response by the student card identifier to isolate
    the admin login card section and the student login card section.
    Admin card appears first (left), student card second (right) in the HTML.
    """
    assert 'id="admin-login-card"' in html, "Admin login card missing from response"
    assert 'id="student-login-card"' in html, "Student login card missing from response"
    parts = html.split('id="student-login-card"')
    admin_section = parts[0]
    student_section = parts[1]
    return student_section, admin_section


@pytest.mark.django_db
class TestDualCardLogin:
    """
    Test suite for the dual-card login interface at /accounts/login/.
    Verifies side-by-side authentication, role isolation before login,
    error scoping strictly to submitted card, username retention,
    and safe next URL validation.
    """

    @pytest.fixture
    def student_user(self):
        return User.objects.create_user(
            username="student_alice",
            password="StrongPassword123!",
            role="student"
        )

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_user(
            username="admin_bob",
            password="StrongPassword123!",
            role="admin",
            is_staff=True
        )

    # 1. Student logs in through the Student card
    def test_student_login_via_student_card_success(self, client, student_user):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'student_alice',
            'password': 'StrongPassword123!'
        })
        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')
        assert client.session['_auth_user_id'] == str(student_user.id)

    # 2. Admin logs in through the Admin card
    def test_admin_login_via_admin_card_success(self, client, admin_user):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'admin',
            'username': 'admin_bob',
            'password': 'StrongPassword123!'
        })
        assert response.status_code == 302
        assert response.url == reverse('accounts:admin_overview')
        assert client.session['_auth_user_id'] == str(admin_user.id)

    # 3. Student blocked on Admin card
    def test_student_blocked_on_admin_card(self, client, student_user):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'admin',
            'username': 'student_alice',
            'password': 'StrongPassword123!'
        })
        assert response.status_code == 200
        # Ensure user was NOT logged in (no session created)
        assert '_auth_user_id' not in client.session

        expected_error = "This account is not an admin account. Use the Student login."
        student_card, admin_card = get_card_contents(response.content.decode())

        # Error must appear only in the Admin card
        assert expected_error in admin_card
        assert expected_error not in student_card

        # Username must stay filled in the Admin card
        assert 'value="student_alice"' in admin_card

    # 4. Admin blocked on Student card
    def test_admin_blocked_on_student_card(self, client, admin_user):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'admin_bob',
            'password': 'StrongPassword123!'
        })
        assert response.status_code == 200
        # Ensure user was NOT logged in (no session created)
        assert '_auth_user_id' not in client.session

        expected_error = "This account is not a student account. Use the Admin login."
        student_card, admin_card = get_card_contents(response.content.decode())

        # Error must appear only in the Student card
        assert expected_error in student_card
        assert expected_error not in admin_card

        # Username must stay filled in the Student card
        assert 'value="admin_bob"' in student_card

    # 5. Wrong password shows the error in the right card (Student card)
    def test_wrong_password_shows_error_in_student_card(self, client, student_user):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'student_alice',
            'password': 'WrongPasswordXYZ!'
        })
        assert response.status_code == 200
        assert '_auth_user_id' not in client.session

        generic_error = "Invalid username or password"
        student_card, admin_card = get_card_contents(response.content.decode())

        assert generic_error in student_card
        assert generic_error not in admin_card
        assert 'value="student_alice"' in student_card

    # 6. Wrong password shows the error in the right card (Admin card)
    def test_wrong_password_shows_error_in_admin_card(self, client, admin_user):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'admin',
            'username': 'admin_bob',
            'password': 'WrongPasswordXYZ!'
        })
        assert response.status_code == 200
        assert '_auth_user_id' not in client.session

        generic_error = "Invalid username or password"
        student_card, admin_card = get_card_contents(response.content.decode())

        assert generic_error in admin_card
        assert generic_error not in student_card
        assert 'value="admin_bob"' in admin_card

    # 7. Non-existent username shows generic error (does not reveal existence)
    def test_nonexistent_username_shows_generic_error(self, client):
        response = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'non_existent_user',
            'password': 'SomePassword123!'
        })
        assert response.status_code == 200
        assert '_auth_user_id' not in client.session

        generic_error = "Invalid username or password"
        student_card, admin_card = get_card_contents(response.content.decode())
        assert generic_error in student_card
        assert generic_error not in admin_card

    # 8. Logged-in user is redirected away from login page
    def test_logged_in_student_redirected_from_login_page(self, client, student_user):
        client.force_login(student_user)
        response = client.get(reverse('accounts:login'))
        assert response.status_code == 302
        assert response.url == reverse('accounts:student_dashboard')

    def test_logged_in_admin_redirected_from_login_page(self, client, admin_user):
        client.force_login(admin_user)
        response = client.get(reverse('accounts:login'))
        assert response.status_code == 302
        assert response.url == reverse('accounts:admin_overview')

    # 9. Test safe next URL handling:
    # covers: safe internal URL, external evil URL, student sent to admin URL, admin sent to student URL
    def test_safe_next_url_handling(self, client, student_user, admin_user):
        # Case A: Safe internal URL (/jobs/)
        student_safe_res = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'student_alice',
            'password': 'StrongPassword123!',
            'next': '/jobs/'
        })
        assert student_safe_res.status_code == 302
        assert student_safe_res.url == '/jobs/'
        client.logout()

        admin_safe_res = client.post(reverse('accounts:login'), {
            'login_type': 'admin',
            'username': 'admin_bob',
            'password': 'StrongPassword123!',
            'next': '/jobs/'
        })
        assert admin_safe_res.status_code == 302
        assert admin_safe_res.url == '/jobs/'
        client.logout()

        # Case B: External URL (https://evil.com) -> ignored, fallback to own dashboard
        student_evil_res = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'student_alice',
            'password': 'StrongPassword123!',
            'next': 'https://evil.com'
        })
        assert student_evil_res.status_code == 302
        assert student_evil_res.url == reverse('accounts:student_dashboard')
        client.logout()

        admin_evil_res = client.post(reverse('accounts:login'), {
            'login_type': 'admin',
            'username': 'admin_bob',
            'password': 'StrongPassword123!',
            'next': 'https://evil.com'
        })
        assert admin_evil_res.status_code == 302
        assert admin_evil_res.url == reverse('accounts:admin_overview')
        client.logout()

        # Case C: Student sent to admin-only URL -> ignored, goes to student dashboard
        student_admin_url_res = client.post(reverse('accounts:login'), {
            'login_type': 'student',
            'username': 'student_alice',
            'password': 'StrongPassword123!',
            'next': '/accounts/admin-overview/'
        })
        assert student_admin_url_res.status_code == 302
        assert student_admin_url_res.url == reverse('accounts:student_dashboard')
        client.logout()

        # Case D: Admin sent to student-only URL -> ignored, goes to admin overview
        admin_student_url_res = client.post(reverse('accounts:login'), {
            'login_type': 'admin',
            'username': 'admin_bob',
            'password': 'StrongPassword123!',
            'next': '/resumes/match/'
        })
        assert admin_student_url_res.status_code == 302
        assert admin_student_url_res.url == reverse('accounts:admin_overview')
        client.logout()
