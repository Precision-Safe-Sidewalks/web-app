from django.db import models


class SurveyorManager(models.Manager):
    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.SURVEYOR)


class BDMManager(models.Manager):
    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.BDM)


class BDAManager(models.Manager):
    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.BDA)
