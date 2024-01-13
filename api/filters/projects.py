import django_filters

from repairs.models import Project


class ProjectFilter(django_filters.FilterSet):
    """Project API filters"""

    class Meta:
        model = Project
        fields = ("arcgis_item", "customer")
