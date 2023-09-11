import factory
import factory.fuzzy

from accounts.factories import UserFactory
from core.factories import TerritoryFactory
from customers.factories import CustomerFactory
from repairs.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)
    customer = factory.SubFactory(CustomerFactory)
    territory = factory.SubFactory(TerritoryFactory)
    business_development_manager = factory.SubFactory(UserFactory)

    class Meta:
        model = Project
