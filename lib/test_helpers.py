from django.test import Client, TestCase

from accounts.factories import UserFactory
from accounts.models import UserRole


class IntegrationTestBase(TestCase):
    """Base integration test class"""

    def setUp(self):
        """Set up the integration tests"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

        # Create a BDM, BDA, and Surveyor
        self.bdm = UserFactory.create_with_roles([UserRole.Role.BDM])
        self.bda = UserFactory.create_with_roles([UserRole.Role.BDA])
        self.surveyor = UserFactory.create_with_roles([UserRole.Role.SURVEYOR])
