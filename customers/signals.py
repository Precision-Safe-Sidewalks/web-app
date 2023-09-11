from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.validators import PhoneNumberValidator
from customers.models import Contact


@receiver(pre_save, sender=Contact)
def format_phone_number(sender, instance, **kwargs):
    """Format the Contact's phone number"""

    if instance.phone_number:
        instance.phone_number = PhoneNumberValidator.format(instance.phone_number)
