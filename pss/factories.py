import factory

from pss.models import Contact, Customer, Territory


class TerritoryFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)
    label = factory.fuzzy.FuzzyText(length=5)

    class Meta:
        model = Territory


class CustomerFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=20)

    class Meta:
        model = Customer


class ContactFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = Contact
