from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        SUPERVISOR = "SUPERVISOR", "Farm Manager / Supervisor"
        STAFF = "STAFF", "Farm Staff"
        VIEWER = "VIEWER", "Viewer"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    phone_number = models.CharField(max_length=20, blank=True)
    unit = models.CharField(max_length=100, blank=True, help_text="Farm unit or department")

    def is_supervisor_or_admin(self):
        return self.role in (self.Role.ADMIN, self.Role.SUPERVISOR)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
