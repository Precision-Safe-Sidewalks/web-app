from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import BDAManager, BDMManager, SurveyorManager


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    objects = models.Manager()
    bdm = BDMManager()
    bda = BDAManager()
    surveyors = SurveyorManager()

    @property
    def initials(self):
        return self.first_name[0].upper() + self.last_name[0].upper()

    def __str__(self):
        return self.full_name

    def save(self, **kwargs):
        if not self.username:
            self.username = self.email

        self.full_name = f"{self.first_name} {self.last_name}"

        return super().save(**kwargs)


class UserRole(models.Model):
    """Role a User performs"""

    class Role(models.TextChoices):
        """Role type choices"""

        BDM = ("BDM", "Business development manager")
        BDA = ("BDA", "Business development administrator")
        SURVEYOR = ("SURVEYOR", "Surveyor")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=50, choices=Role.choices)

    class Meta:
        unique_together = ("user", "role")
