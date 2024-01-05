import factory
import factory.fuzzy

from customers.factories import CustomerFactory
from repairs.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)
    customer = factory.SubFactory(CustomerFactory)

    class Meta:
        model = Project
