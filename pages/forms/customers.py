from django import forms
from django.contrib.auth import get_user_model

from core.models import Territory
from customers.models import Customer


User = get_user_model()


class CustomerForm(forms.ModelForm):
    territory = forms.ModelChoiceField(
        queryset=Territory.objects.order_by("name"), required=True
    )
    business_development_manager = forms.ModelChoiceField(
        queryset=User.bdm.order_by("full_name"), required=True
    )

    class Meta:
        model = Customer
        fields = (
            "name",
            "address",
            "city",
            "state",
            "segment",
            "business_development_manager",
            "territory",
        )
