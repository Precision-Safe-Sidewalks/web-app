from django.contrib.auth import get_user_model
from django.db.models import Case, Max, Min, Value, When
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
from repairs.models import Measurement, Project
from repairs.models.constants import Stage

User = get_user_model()


class SortMixin:
    """Mixin to dynamically handle sort order"""

    def get_queryset(self):
        queryset = super().get_queryset()

        if sort := self.request.GET.get("sort"):
            queryset = queryset.order_by(sort, "id")

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


class DashboardTableViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DashboardTableSerializer
    filterset_class = DashboardTableFilter

    def get_queryset(self):
        queryset = Project.objects.order_by("id")
        sort = self.request.GET.get("sort")

        if sort:
            if sort.endswith("start_date") or sort.endswith("last_date"):
                ordering = (
                    Measurement.objects.filter(stage=Stage.PRODUCTION)
                    .values("project_id")
                    .annotate(start_date=Min("measured_at"))
                    .annotate(last_date=Max("measured_at"))
                    .order_by(sort)
                )

                args = []

                for index, row in enumerate(ordering):
                    args.append(When(pk=row["project_id"], then=Value(index)))

                queryset = queryset.annotate(
                    ordering=Case(*args, default=Value(len(args)))
                ).order_by("ordering", "id")

            else:
                queryset = queryset.order_by(sort)

        return queryset
