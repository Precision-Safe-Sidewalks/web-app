from django import forms

from customers.models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ("customer", "name", "email", "phone_number")
        widgets = {
            "customer": forms.HiddenInput(),
        }
