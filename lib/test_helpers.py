# ruff: noqa
import factory.faker
import factory.fuzzy
from django.test import TestCase


class IntegrationTestBase(TestCase):
    """Base integration test class"""
