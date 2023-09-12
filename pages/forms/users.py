from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import UserRole

User = get_user_model()


class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    roles = forms.MultipleChoiceField(choices=UserRole.Role.choices, required=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            user = super().save(*args, **kwargs)
            roles = self.cleaned_data["roles"]

            UserRole.objects.exclude(user=user, role__in=roles).delete()

            for role in roles:
                UserRole.objects.get_or_create(user=user, role=role)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_active", "is_staff")
