import factory
import factory.fuzzy

from core.models import Territory


class TerritoryFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=10)
    label = factory.fuzzy.FuzzyText(length=5)

    class Meta:
        model = Territory
