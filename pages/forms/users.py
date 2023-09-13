from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import UserPhoneNumber, UserRole
from core.models.constants import PhoneNumberType
from core.validators import PhoneNumberValidator

User = get_user_model()


class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    roles = forms.MultipleChoiceField(choices=UserRole.Role.choices, required=False)
    phone_work = forms.CharField(max_length=25, required=False)
    phone_work_ext = forms.CharField(max_length=10, required=False)
    phone_cell = forms.CharField(max_length=25, required=False)
    phone_cell_ext = forms.CharField(max_length=10, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["roles"].initial = list(
                self.instance.roles.values_list("role", flat=True)
            )

            if phone_work := self.instance.get_work_phone():
                self.fields["phone_work"].initial = phone_work.phone_number
                self.fields["phone_work_ext"].initial = phone_work.extension

            if phone_cell := self.instance.get_cell_phone():
                self.fields["phone_cell"].initial = phone_cell.phone_number
                self.fields["phone_cell_ext"].initial = phone_cell.extension

    def save(self, *args, **kwargs):
        with transaction.atomic():
            user = super().save(*args, **kwargs)

            # Force all superusers to be staff since there is currently no
            # distinction between the two roles
            if user.is_superuser:
                user.is_staff = True
                user.save()

            self.save_roles(user)
            self.save_phone_number(user, PhoneNumberType.WORK)
            self.save_phone_number(user, PhoneNumberType.CELL)

    def save_roles(self, user):
        """Save the roles for the User"""
        roles = self.cleaned_data["roles"]
        user.roles.exclude(role__in=roles).delete()

        for role in roles:
            UserRole.objects.get_or_create(user=user, role=role)

    def save_phone_number(self, user, number_type):
        """Save a phone number for the User"""
        number = self.cleaned_data[f"phone_{number_type.lower()}"]
        extension = self.cleaned_data[f"phone_{number_type.lower()}_ext"]

        if not number:
            user.phone_numbers.filter(number_type=number_type).delete()
            return

        UserPhoneNumber.objects.update_or_create(
            user=user,
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
        model = User
        fields = ("first_name", "last_name", "email", "is_active", "is_superuser")
