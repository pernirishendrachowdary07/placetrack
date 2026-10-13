from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Seed demo users: one admin (role admin) and one student"

    def handle(self, *args, **options):
        # 1. Admin user
        admin_username = "admin"
        admin_password = "admin123"
        admin_email = "admin@placetrack.local"

        admin_user, created = User.objects.get_or_create(username=admin_username)
        admin_user.set_password(admin_password)
        admin_user.role = "admin"
        admin_user.email = admin_email
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created admin user '{admin_username}' (role: admin)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated existing admin user '{admin_username}' (role: admin)"))

        # 2. Student user
        student_username = "alice_student"
        student_password = "StrongP@ssw0rd123"
        student_email = "alice@placetrack.local"

        student_user, created = User.objects.get_or_create(username=student_username)
        student_user.set_password(student_password)
        student_user.role = "student"
        student_user.email = student_email
        student_user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created student user '{student_username}' (role: student)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated existing student user '{student_username}' (role: student)"))

        self.stdout.write("\n" + "=" * 45)
        self.stdout.write(self.style.SUCCESS("Demo Users Credentials:"))
        self.stdout.write(f"  Admin:   username='{admin_username}', password='{admin_password}', role='admin'")
        self.stdout.write(f"  Student: username='{student_username}', password='{student_password}', role='student'")
        self.stdout.write("=" * 45 + "\n")
