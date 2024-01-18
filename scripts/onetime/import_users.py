import csv

from django.contrib.auth import get_user_model

from accounts.models import UserRole


User = get_user_model()


def import_users(filename):
    """Import users from a CSV"""

    with open(filename, "r") as f:
        for values in csv.DictReader(f):
            email = values.pop("email")
            user, _ = User.objects.get_or_create(email=email)

            user.first_name = values["first_name"]
            user.last_name = values["last_name"]
            user.is_active = True
            user.save()

            if values["bdm"]:
                UserRole.objects.get_or_create(user=user, role=UserRole.Role.BDM)

            if values["bda"]:
                UserRole.objects.get_or_create(user=user, role=UserRole.Role.BDA)

            if values["surveyor"]:
                UserRole.objects.get_or_create(user=user, role=UserRole.Role.SURVEYOR)


if __name__ == "django.core.management.commands.shell":
    filename = "scripts/onetime/pss_users_list.csv"
    import_users(filename)
