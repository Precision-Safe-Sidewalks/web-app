import django_filters

from repairs.models import Measurement


class MeasurementFilter(django_filters.FilterSet):
    """Measurement API filters"""

    class Meta:
        model = Measurement
        fields = ("project", "stage")
