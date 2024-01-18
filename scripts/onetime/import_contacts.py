import csv

from core.models.constants import PhoneNumberType
from core.validators import PhoneNumberValidator
from customers.models import Contact, ContactPhoneNumber, Customer


def import_contacts(filename):
    """Import Contacts from CSVs"""

    with open(filename, "r") as f:
        for values in csv.DictReader(f):
            customer = Customer.objects.get(name=values["Person - Organization"])
            contact, _ = Contact.objects.get_or_create(
                name=values["Person - Name"], customer=customer
            )

            if title := values["Person - Job title"]:
                contact.title = title

            if email := values["Person - Email"]:
                contact.email = email

            if phone := values["Person - Phone"]:
                for i, value in enumerate(phone.split(",")):
                    number_type = "WORK" if i == 0 else "CELL"
                    value = PhoneNumberValidator.format(
                        value.strip(), raise_exception=True
                    )
                    ContactPhoneNumber.objects.get_or_create(
                        contact=contact, number_type=number_type, phone_number=value
                    )

            contact.save()


if __name__ == "django.core.management.commands.shell":
    filename = "scripts/onetime/pss_contacts_list.csv"
    import_contacts(filename)
