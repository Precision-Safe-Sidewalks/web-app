from django import forms
from django.db import transaction

from core.validators import PhoneNumberValidator
from customers.models import Contact, ContactPhoneNumber


class ContactForm(forms.ModelForm):
    phone_work = forms.CharField(max_length=25, required=False)
    phone_work_ext = forms.CharField(max_length=10, required=False)
    phone_cell = forms.CharField(max_length=25, required=False)
    phone_cell_ext = forms.CharField(max_length=10, required=False)

    def save(self, **kwargs):
        with transaction.atomic():
            contact = super().save(**kwargs)
            self.save_phone_number(contact, ContactPhoneNumber.NumberType.WORK)
            self.save_phone_number(contact, ContactPhoneNumber.NumberType.CELL)

    def save_phone_number(self, contact, number_type):
        """Save a phone number for the Contact"""
        number = self.cleaned_data[f"phone_{number_type.lower()}"]
        extension = self.cleaned_data[f"phone_{number_type.lower()}_ext"]

        if not number:
            contact.phone_numbers.filter(number_type=number_type).delete()
            return

        ContactPhoneNumber.objects.update_or_create(
            contact=contact,
            number_type=number_type,
            defaults={
                "phone_number": number,
                "extension": extension.strip() or None,
            },
        )

    def clean_phone_work(self):
        self.clean_phone("work")

    def clean_phone_cell(self):
        self.clean_phone("cell")

    def clean_phone(self, number_type):
        number = self.cleaned_data[f"phone_{number_type}"].strip()

        if number:
            number = PhoneNumberValidator.format(number, raise_exception=True)
            self.cleaned_data[f"phone_{number_type}"] = number
        else:
            self.cleaned_data[f"phone_{number_type}"] = None
            self.cleaned_data[f"phone_{number_type}_ext"] = None

    class Meta:
        model = Contact
        fields = (
            "customer",
            "name",
            "email",
            "phone_work",
            "phone_work_ext",
            "phone_cell",
            "phone_cell_ext",
        )
        widgets = {
            "customer": forms.HiddenInput(),
        }
