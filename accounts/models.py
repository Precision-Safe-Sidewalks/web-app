from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)

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
