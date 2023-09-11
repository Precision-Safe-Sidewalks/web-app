import re

from django.db import models

from core.exceptions import PhoneNumberError
from core.models.constants import RE_PHONE


class AbstractPhoneNumber(models.Model):
    """Abstract phone number"""

    @staticmethod
    def validate(value):
        """Validate a phone number input and return the formatted value"""
        if not RE_PHONE.match(value):
            raise PhoneNumberError

        value = re.sub("[\(\)\-\s]", "", value)
        return f"({value[:3]}) {value[3:6]}-{value[6:]}"
