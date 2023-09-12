from django.db import models

from core.models.constants import States
from core.validators import PhoneNumberValidator


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
        return self.phone_numbers.filter(
            number_type=ContactPhoneNumber.NumberType.WORK
        ).first()

    def get_cell_phone(self):
        """Return the cell phone number"""
        return self.phone_numbers.filter(
            number_type=ContactPhoneNumber.NumberType.CELL
        ).first()

    def __str__(self):
        return f"{self.customer.name} - {self.name}"


class ContactPhoneNumber(models.Model):
    """Contact phone number"""

    class NumberType(models.TextChoices):
        """Phone number type choices"""

        CELL = ("CELL", "Cell")
        WORK = ("WORK", "Work")

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="phone_numbers"
    )
    number_type = models.CharField(max_length=10, choices=NumberType.choices)
    phone_number = models.CharField(max_length=25, validators=[PhoneNumberValidator])
    extension = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.extension:
            return f"{self.phone_number} ext. {self.extension}"
        return self.phone_number
