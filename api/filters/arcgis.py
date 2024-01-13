import django_filters

from third_party.models import ArcGISItem


class ArcGISItemFilter(django_filters.FilterSet):
    """ArcGIS Item filter set"""

    class Meta:
        model = ArcGISItem
        fields = ("item_id", "item_type", "parent")
