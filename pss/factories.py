import factory
import factory.fuzzy

from pss.models import Contact, Customer


class CustomerFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=20)

    class Meta:
        model = Customer


class ContactFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = Contact
