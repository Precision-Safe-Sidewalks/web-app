import django_filters
from django.db.models import Q

from third_party.models import ArcGISItem


class ArcGISItemFilter(django_filters.FilterSet):
    """ArcGIS Item filter set"""

    autocomplete = django_filters.CharFilter(method="filter_autocomplete")

    def filter_autocomplete(self, queryset, name, value):
        """Filter by the autocomplete query"""
        return queryset.filter(title__istartswith=value)

    class Meta:
        model = ArcGISItem
        fields = ("item_id", "item_type", "parent")
