from django.contrib.auth import get_user_model
from rest_framework import viewsets

from api.filters.tables import (
    ContactTableFilter,
    CustomerTableFilter,
    DashboardTableFilter,
    ProjectTableFilter,
    UserTableFilter,
)
from api.serializers.tables import (
    ContactTableSerializer,
    CustomerTableSerializer,
    DashboardTableSerializer,
    ProjectTableSerializer,
    UserTableSerializer,
)
from customers.models import Contact, Customer
from repairs.models import Project, ProjectManagementDashboardView

User = get_user_model()


class SortMixin:
    """Mixin to dynamically handle sort order"""

    def get_queryset(self):
        queryset = super().get_queryset()

        if sort := self.request.GET.get("sort"):
            queryset = queryset.order_by(sort)

        return queryset


class ContactTableViewSet(SortMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.order_by("id")
    serializer_class = ContactTableSerializer
    filterset_class = ContactTableFilter


class CustomerTableViewSet(SortMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.order_by("id")
    serializer_class = CustomerTableSerializer
    filterset_class = CustomerTableFilter


class ProjectTableViewSet(SortMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.order_by("id")
    serializer_class = ProjectTableSerializer
    filterset_class = ProjectTableFilter


class UserTableViewSet(SortMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.order_by("id")
    serializer_class = UserTableSerializer
    filterset_class = UserTableFilter


class DashboardTableViewSet(SortMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ProjectManagementDashboardView.objects.order_by("project_id")
    serializer_class = DashboardTableSerializer
    filterset_class = DashboardTableFilter
