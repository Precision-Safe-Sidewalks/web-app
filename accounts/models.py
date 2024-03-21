from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from accounts.managers import BDAManager, BDMManager, SurveyorManager, TechManager
from core.models.abstract import AbstractPhoneNumber
from core.models.constants import PhoneNumberType


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    initials = models.CharField(max_length=2, blank=True, null=True)
    arcgis_username = models.CharField(max_length=100, blank=True, null=True)

    objects = UserManager()
    bdm = BDMManager()
    bda = BDAManager()
    surveyors = SurveyorManager()
    techs = TechManager()

    def get_initials(self):
        if self.first_name and self.last_name:
            return self.first_name[0].upper() + self.last_name[0].upper()
        return None

    def __str__(self):
        return self.full_name

    def save(self, **kwargs):
        if not self.username:
            self.username = self.email

        self.full_name = f"{self.first_name} {self.last_name}"
        self.initials = self.get_initials()

        return super().save(**kwargs)

    def get_work_phone(self):
        """Return the work phone for the User"""
        return self.phone_numbers.filter(number_type=PhoneNumberType.WORK).first()

    def get_cell_phone(self):
        """Return the cell phone for the User"""
        return self.phone_numbers.filter(number_type=PhoneNumberType.CELL).first()


class UserRole(models.Model):
    """Role a User performs"""

    class Role(models.TextChoices):
        """Role type choices"""

        BDM = ("BDM", "Business development manager")
        BDA = ("BDA", "Business development administrator")
        SURVEYOR = ("SURVEYOR", "Surveyor")
        TECH = ("TECH", "Tech")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=50, choices=Role.choices)

    class Meta:
        unique_together = ("user", "role")


class UserPhoneNumber(AbstractPhoneNumber):
    """Phone number for a user"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="phone_numbers"
    )
