from django.contrib.auth import get_user_model
from django.db import models

from core.models.abstract import AbstractPhoneNumber
from core.models import Territory
from core.models.constants import PhoneNumberType, States
from customers.constants import Segment


User = get_user_model()


class Customer(models.Model):
    """External client or municipality"""

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(
        max_length=2, blank=True, null=True, choices=States.choices
    )
    segment = models.CharField(
        max_length=100, choices=Segment.choices, blank=True, null=True
    )
    business_development_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True
    )
    territory = models.ForeignKey(
        Territory, on_delete=models.SET_NULL, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def short_address(self):
        """Return the city, state address"""
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        return None

    @property
    def active_projects(self):
        """Return the Projects currently in progress"""
        from repairs.models.projects import Project

        return self.projects.exclude(status=Project.Status.COMPLETE).order_by(
            "created_at"
        )

    @property
    def completed_projects(self):
        """Return the Projects that have been completed"""
        from repairs.models.projects import Project

        return self.projects.filter(status=Project.Status.COMPLETE).order_by(
            "created_at"
        )


class Contact(models.Model):
    """Contact information for an external person"""

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="contacts"
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(
        max_length=2, choices=States.choices, blank=True, null=True
    )
    zip_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_phone_number(self):
        """Return the Work or Cell phone number"""
        if phone := self.get_work_phone():
            return phone

        return self.get_cell_phone()

    def get_work_phone(self):
        """Return the work phone number"""
        return self.phone_numbers.filter(number_type=PhoneNumberType.WORK).first()

    def get_cell_phone(self):
        """Return the cell phone number"""
        return self.phone_numbers.filter(number_type=PhoneNumberType.CELL).first()

    def __str__(self):
        return self.name


class ContactPhoneNumber(AbstractPhoneNumber):
    """Contact phone number"""

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="phone_numbers"
    )
