from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters.measurements import MeasurementFilter
from api.serializers.measurements import MeasurementSerializer
from repairs.models import Measurement


class MeasurementViewSet(ReadOnlyModelViewSet):
    """Read-only view set for a Project's Measurements"""

    queryset = Measurement.objects.order_by("id")
    serializer_class = MeasurementSerializer
    filterset_class = MeasurementFilter
