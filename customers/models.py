from django.db import models

from core.models.abstract import AbstractPhoneNumber
from core.models.constants import PhoneNumberType, States


class Customer(models.Model):
    """External client or municipality"""

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(
        max_length=2, blank=True, null=True, choices=States.choices
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

        return self.projects.filter(status=Project.Status.STARTED).order_by(
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
    email = models.EmailField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: add notes

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
