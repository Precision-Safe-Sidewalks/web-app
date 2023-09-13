from django.db import models

from core.models.constants import PhoneNumberType
from core.validators import PhoneNumberValidator


class AbstractPhoneNumber(models.Model):
    """Abstract phone number for an entity"""

    number_type = models.CharField(max_length=10, choices=PhoneNumberType.choices)
    phone_number = models.CharField(max_length=25, validators=[PhoneNumberValidator])
    extension = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.extension:
            return f"{self.phone_number} ext. {self.extension}"
        return self.phone_number

    class Meta:
        abstract = True
