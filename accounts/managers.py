from django.db import models


class SurveyorManager(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.SURVEYOR)


class BDMManager(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.BDM)

    def to_options(self):
        """Return the list of options dictionaries"""
        queryset = self.get_queryset().order_by("full_name")
        return [{"key": u.id, "value": u.full_name} for u in queryset]


class BDAManager(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.BDA)


class TechManager(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        from accounts.models import UserRole

        return super().get_queryset().filter(roles__role=UserRole.Role.TECH)
