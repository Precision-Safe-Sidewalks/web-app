import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from customers.models import Contact, Customer
from repairs.models import Project

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

    def filter_q(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    class Meta:
        model = Customer
        fields = ("q",)


class ProjectTableFilter(django_filters.FilterSet):
    """Project data table filters"""

    q = django_filters.CharFilter(method="filter_q")
    status = django_filters.MultipleChoiceFilter(choices=Project.Status.choices)

    def filter_q(self, queryset, name, value):
        # TODO: make BD/BDA filterable

        return queryset.filter(
            Q(name__icontains=value)
            | Q(territory__label__icontains=value)
            | Q(territory__name__icontains=value)
        )

    class Meta:
        model = Project
        fields = ("customer", "status", "q")


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
