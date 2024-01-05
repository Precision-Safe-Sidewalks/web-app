import factory
import factory.fuzzy

from accounts.factories import UserFactory
from core.factories import TerritoryFactory
from customers.models import Contact, Customer


class CustomerFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=20)
    territory = factory.SubFactory(TerritoryFactory)
    business_development_manager = factory.SubFactory(UserFactory)

    class Meta:
        model = Customer


class ContactFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = Contact
