from django import forms
from django.db import transaction

from core.models.constants import PhoneNumberType
from core.validators import PhoneNumberValidator
from customers.models import Contact, ContactPhoneNumber


class ContactForm(forms.ModelForm):
    phone_work = forms.CharField(max_length=25, required=False)
    phone_work_ext = forms.CharField(max_length=10, required=False)
    phone_cell = forms.CharField(max_length=25, required=False)
    phone_cell_ext = forms.CharField(max_length=10, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            if phone_work := self.instance.get_work_phone():
                self.fields["phone_work"].initial = phone_work.phone_number
                self.fields["phone_work_ext"].initial = phone_work.extension

            if phone_cell := self.instance.get_cell_phone():
                self.fields["phone_cell"].initial = phone_cell.phone_number
                self.fields["phone_cell_ext"].initial = phone_cell.extension

    def save(self, **kwargs):
        with transaction.atomic():
            contact = super().save(**kwargs)
            self.save_phone_number(contact, PhoneNumberType.WORK)
            self.save_phone_number(contact, PhoneNumberType.CELL)

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
        number = self.clean_phone("work")
        return number

    def clean_phone_cell(self):
        number = self.clean_phone("cell")
        return number

    def clean_phone(self, number_type):
        number = self.cleaned_data[f"phone_{number_type}"].strip()

        if not number:
            return None

        return PhoneNumberValidator.format(number, raise_exception=True)

    class Meta:
        model = Contact
        fields = (
            "customer",
            "name",
            "email",
            "notes",
            "phone_work",
            "phone_work_ext",
            "phone_cell",
            "phone_cell_ext",
        )
        widgets = {
            "customer": forms.HiddenInput(),
            "notes": forms.TextInput(),
        }
