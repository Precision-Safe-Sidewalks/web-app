from django import forms
from django.contrib.auth import get_user_model

from customers.models import Contact, Customer
from repairs.models import Project

User = get_user_model()


class ProjectForm(forms.ModelForm):
    business_development_manager = forms.ModelChoiceField(
        queryset=User.bdm.order_by("full_name")
    )
    business_development_administrator = forms.ModelChoiceField(
        queryset=User.bda.order_by("full_name"), required=False
    )
    primary_contact = forms.ModelChoiceField(queryset=Contact.objects.order_by("name"))
    secondary_contact = forms.ModelChoiceField(
        queryset=Contact.objects.order_by("name"), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        customer_id = self.initial["customer"]

        if customer_id:
            customer = Customer.objects.get(pk=customer_id)
            self.fields["primary_contact"].queryset = customer.contacts.order_by("name")
            self.fields["secondary_contact"].queryset = customer.contacts.order_by(
                "name"
            )

    def save(self, commit=True):
        """Save the Project and Contact information"""
        project = super().save(commit=False)

        if commit:
            project.save()
            project.set_contact(self.cleaned_data["primary_contact"], order=0)
            project.set_contact(self.cleaned_data["secondary_contact"], order=1)

        return project

    class Meta:
        model = Project
        fields = (
            "customer",
            "name",
            "address",
            "business_development_manager",
            "business_development_administrator",
            "territory",
            "pricing_model",
            "po_number",
            "primary_contact",
            "secondary_contact",
        )
        widgets = {
            "customer": forms.HiddenInput(),
            "address": forms.TextInput(),
        }


class ProjectMeasurementsForm(forms.Form):
    """Project measurements CSV upload"""

    file = forms.FileField(widget=forms.FileInput(attrs={"accept": "text/csv"}))
