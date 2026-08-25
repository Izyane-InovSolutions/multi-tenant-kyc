from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = "Create system admin users for tenant management"

    def handle(self, *args, **kwargs):
        admins = [
            {
                "username": "admin1@izyane.com",
                "email": "admin1@izyane.com",
                "password": "ChangeMe@123",
                "first_name": "System",
                "last_name": "Admin One",
            },
            {
                "username": "admin2@izyane.com",
                "email": "admin2@izyane.com",
                "password": "ChangeMe@123",
                "first_name": "System",
                "last_name": "Admin Two",
            },
        ]

        for admin in admins:
            if User.objects.filter(username=admin["username"]).exists():
                self.stdout.write(
                    self.style.WARNING(f"Admin already exists (username): {admin['username']}")
                )
                continue

            if User.objects.filter(email__iexact=admin["email"]).exists():
                self.stdout.write(
                    self.style.WARNING(f"Admin already exists (email): {admin['email']}")
                )
                continue

            try:
                User.objects.create_superuser(
                    username=admin["username"],
                    email=admin["email"],
                    password=admin["password"],
                    first_name=admin["first_name"],
                    last_name=admin["last_name"],
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created admin: {admin['email']}")
                )
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create {admin['email']}: {e}")
                )