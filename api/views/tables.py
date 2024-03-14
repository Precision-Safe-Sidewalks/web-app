from datetime import datetime, timedelta

from dateutil.parser import parse as parse_dt
from django.contrib.auth import get_user_model
from django.db import connection
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


class TechProductionDashboardTableViewSet(viewsets.ViewSet):
    """Tech production dashboard table view set"""

    def list(self, request):
        """List the tech production between the start/end dates"""
        start_date = self._get_date(request, "start_date")
        end_date = self._get_date(request, "end_date")

        if not (start_date and end_date):
            data = {"detail": "start_date and end_date are required"}
            return Response(data, status=400)

        days = (end_date - start_date).days

        if days <= 0 or days > 100:
            data = {
                "detail": "start_date must be before and within 100 days of end_date"
            }
            return Response(data, status=400)

        data = self._get_data(start_date, end_date)

        return Response(data)

    def _get_date(self, request, key):
        """Get the date query parameter"""
        value = request.GET.get(key)

        if value is None:
            return None

        try:
            return parse_dt(value).date()
        except:
            return None

    def _get_data(self, start_date, end_date):
        """Get the data for the dashboard"""
        days = (end_date - start_date).days

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        columns = [
            "tech",
            "COALESCE(SUM(inch_feet), 0) AS total_inch_feet",
            "COALESCE(COUNT(id), 0) AS total_records",
            "COALESCE(COUNT(DISTINCT(DATE(measured_at))), 0) AS days_worked",
        ]

        for day in range(days):
            key = f"date_{day}"
            date = start_date + timedelta(days=day)
            params[key] = date

            column = f'SUM(inch_feet) FILTER(WHERE DATE(measured_at) = %({key})s) AS "{date}"'
            columns.append(column)

        query = f"""
            SELECT
                {", ".join(columns)}
            FROM repairs_measurement 
            WHERE measured_at >= %(start_date)s
                AND measured_at <= %(end_date)s
            GROUP by tech 
            ORDER BY tech
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params=params)
            columns = [column.name for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            for row in results:
                days_worked = row["days_worked"]
                total_inch_feet = row["total_inch_feet"]

                if days_worked > 0:
                    row["average_per_day"] = total_inch_feet / days_worked
                else:
                    row["average_per_day"] = None

        return results
