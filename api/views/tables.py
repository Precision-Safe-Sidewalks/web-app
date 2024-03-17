from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response

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
from lib.pay_periods import get_pay_period_dates
from repairs.models import Measurement, Project, ProjectManagementDashboardView

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


class TechProductionDashboardTableViewSet(viewsets.ViewSet):
    """Tech production dashboard table view set"""

    _columns = {
        "tech": "Tech",
        "total_inch_feet": "Total",
        "total_days": "# Days Worked",
        "average_per_day": "Avg/Day",
        "total_records": "# Records",
    }

    def list(self, request):
        """List the tech production between the start/end dates"""
        period = int(request.GET.get("period", 0))
        techs = request.GET.getlist("tech", [])

        start_date, end_date = get_pay_period_dates(period)
        data = Measurement.get_tech_production(start_date, end_date, techs=techs)

        for row in data:
            date_keys = [key for key in row if key not in self._columns]
            keys = (
                ["tech"]
                + date_keys
                + ["total_inch_feet", "total_days", "average_per_day", "total_records"]
            )

            for key in keys:
                if key in self._columns:
                    label = self._columns[key]
                else:
                    (year, month, day) = key.split("-")
                    label = f"{month}/{day}/{year}"

                row[label] = row.pop(key)

                if isinstance(row[label], float):
                    row[label] = round(row[label], 2)

        return Response(data)
