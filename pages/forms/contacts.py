from django import forms

from core.validators import PhoneNumberValidator
from customers.models import Contact


class ContactForm(forms.ModelForm):

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
