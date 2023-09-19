import factory
import factory.fuzzy
from django.contrib.auth import get_user_model

from accounts.models import UserRole


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.fuzzy.FuzzyText(length=10)
    email = factory.Faker("email")
    is_active = True

    @classmethod
    def create_with_roles(cls, roles=[], **kwargs):
        """Create a user with roles"""
        user = cls(**kwargs)

        for role in roles:
            UserRole.objects.create(user=user, role=role)

        return user

    class Meta:
        model = get_user_model()
