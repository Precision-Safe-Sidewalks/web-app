import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers.phonenumberutil import NumberParseException


class PhoneNumberValidator:
    """Phone number validator"""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, value):
        self.validate(value)

    @staticmethod
    def validate(value, raise_exception=True):
        """Validate the phone number"""
        try:
            number = phonenumbers.parse(value, "US")

            if not phonenumbers.is_valid_number(number):
                raise NumberParseException("", "")

        except NumberParseException:
            if raise_exception:
                raise ValidationError("Enter a valid phone number.")
            return False

        return True

    @staticmethod
    def format(value, raise_exception=False):
        """Return the formatted phone number"""
        if PhoneNumberValidator.validate(value, raise_exception=raise_exception):
            number = phonenumbers.parse(value, "US")
            value = str(number.national_number)
            return f"{value[:3]}-{value[3:6]}-{value[6:]}"
