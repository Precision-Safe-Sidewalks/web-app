import csv
import re

from django.contrib.auth import get_user_model

from customers.models import Customer
from core.models import Territory


User = get_user_model()

RE_ADDRESS_V1 = re.compile(
    r"(?P<address>.*), (?P<city>.*), (?P<state>[A-Z]{2}) (?P<zip_code>\d{5}), USA"
)
RE_ADDRESS_V2 = re.compile(
    r"(?P<city>.*), (?P<state>[A-Z]{2}) (?P<zip_code>\d{5}), USA"
)
RE_ADDRESS_V3 = re.compile(r"(?P<city>.*), (?P<state>[A-Z]{2}), USA")


def import_organizations(filename):
    """Import Organizations from CSVs"""

    SEGMENTS = {
        "Municipal Small": "Muni Small",
        "Municipal Large": "Muni Large",
    }

    with open(filename, "r") as f:
        for values in csv.DictReader(f):
            customer, _ = Customer.objects.get_or_create(
                name=values["Organization - Name"]
            )
            customer.segment = SEGMENTS[values["Organization - Segment"]]

            if address := values["Organization - Full/combined address of Address"]:
                for expr in (RE_ADDRESS_V1, RE_ADDRESS_V2, RE_ADDRESS_V3):
                    if match := expr.match(address):
                        for key, value in match.groupdict().items():
                            setattr(customer, key, value)
                        break

            territory = Territory.objects.get(label=values["Territory"])
            customer.territory = territory

            bdm = User.objects.filter(full_name=values["Organization - Owner"]).first()
            customer.business_development_manager = bdm

            customer.save()


if __name__ == "django.core.management.commands.shell":
    filename = "scripts/onetime/pss_organizations_list.csv"
    import_organizations(filename)
