from django.contrib.auth import get_user_model
from rest_framework import viewsets

from api.filters.tables import (
    ContactTableFilter,
    CustomerTableFilter,
    ProjectTableFilter,
    UserTableFilter,
)
from api.serializers.tables import (
    ContactTableSerializer,
    CustomerTableSerializer,
    ProjectTableSerializer,
    UserTableSerializer,
)
from customers.models import Contact, Customer
from repairs.models import Project

User = get_user_model()


class ContactTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.order_by("id")
    serializer_class = ContactTableSerializer
    filterset_class = ContactTableFilter


class CustomerTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.order_by("id")
    serializer_class = CustomerTableSerializer
    filterset_class = CustomerTableFilter


class ProjectTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.order_by("id")
    serializer_class = ProjectTableSerializer
    filterset_class = ProjectTableFilter


class UserTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.order_by("id")
    serializer_class = UserTableSerializer
    filterset_class = UserTableFilter
