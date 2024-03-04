import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from core.models import Territory
from customers.constants import Segment
from customers.models import Contact, Customer
from repairs.models import Project, ProjectDashboard

User = get_user_model()


class ContactTableFilter(django_filters.FilterSet):
    """Contact data table filters"""

    q = django_filters.CharFilter(method="filter_q")

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(email__icontains=value))

    class Meta:
        model = Contact
        fields = ("customer", "q")


class CustomerTableFilter(django_filters.FilterSet):
    """Customer data table filters"""

    q = django_filters.CharFilter(method="filter_q")
    business_development_manager = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
    )
    segment = django_filters.MultipleChoiceFilter(
        field_name="segment",
        choices=Segment.choices,
    )
    territory = django_filters.ModelMultipleChoiceFilter(
        queryset=Territory.objects.all(),
    )

    def filter_q(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    class Meta:
        model = Customer
        fields = (
            "business_development_manager",
            "territory",
            "segment",
            "q",
        )


class ProjectTableFilter(django_filters.FilterSet):
    """Project data table filters"""

    q = django_filters.CharFilter(method="filter_q")
    active = django_filters.BooleanFilter(method="filter_active")
    status = django_filters.MultipleChoiceFilter(choices=Project.Status.choices)
    business_development_manager = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
    )
    segment = django_filters.MultipleChoiceFilter(
        field_name="customer__segment",
        choices=Segment.choices,
    )
    territory = django_filters.ModelMultipleChoiceFilter(
        queryset=Territory.objects.all(),
    )

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(business_development_manager__full_name__icontains=value)
            | Q(customer__segment__icontains=value)
            | Q(territory__label__icontains=value)
            | Q(territory__name__icontains=value)
        )

    def filter_active(self, queryset, name, value):
        if value is True:
            return queryset.exclude(status=Project.Status.COMPLETE)

        if value is False:
            return queryset.filter(status=Project.Status.COMPLETE)

        return queryset

    class Meta:
        model = Project
        fields = (
            "customer",
            "status",
            "business_development_manager",
            "segment",
            "territory",
            "q",
        )


class UserTableFilter(django_filters.FilterSet):
    """User data table filters"""

    q = django_filters.CharFilter(method="filter_q")

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) | Q(email__icontains=value)
        )

    class Meta:
        model = User
        fields = ("q",)


class DashboardTableFilter(django_filters.FilterSet):
    """Dashboard data table filters"""

    business_development_manager = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        method="filter_business_development_manager",
    )
    territory = django_filters.ModelMultipleChoiceFilter(
        queryset=Territory.objects.all(),
        method="filter_territory",
    )
    status = django_filters.MultipleChoiceFilter(
        field_name="status", choices=Project.Status.choices
    )

    def filter_business_development_manager(self, queryset, name, value):
        if value:
            bd_ids = [bd.id for bd in value]
            queryset = queryset.filter(bd_id__in=bd_ids)
        return queryset

    def filter_territory(self, queryset, name, value):
        if value:
            territory_ids = [territory.id for territory in value]
            queryset = queryset.filter(territory_id__in=territory_ids)
        return queryset

    class Meta:
        model = ProjectDashboard
        fields = ("business_development_manager", "territory", "status")
