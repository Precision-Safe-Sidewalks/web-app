from django import forms

from core.validators import PhoneNumberValidator
from customers.models import Contact


class ContactForm(forms.ModelForm):
    phone_work = models.CharField(max_length=25, required=False)
    phone_work_ext = models.CharField(max_length=10, required=False)
    phone_cell = models.CharField(max_length=25, required=False)
    phone_cell_ext = models.CharField(max_length=10, required=False)

    def clean_phone_work(self):
        raise NotImplementedError

    def clean_phone_cell(self):
        raise NotImplementedError

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]

        if phone_number:
            PhoneNumberValidator.validate(phone_number)

        return phone_number

    class Meta:
        model = Contact
        fields = ("customer", "name", "email")
        widgets = {
            "customer": forms.HiddenInput(),
        }
