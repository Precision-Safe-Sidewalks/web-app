from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.templatetags.static import static

from api.filters.measurements import MeasurementFilter
from api.serializers.measurements import MeasurementSerializer
from repairs.models import Measurement
from repairs.models.constants import SYMBOLS


class MeasurementViewSet(ReadOnlyModelViewSet):
    """Read-only view set for a Project's Measurements"""

    queryset = Measurement.objects.order_by("id")
    serializer_class = MeasurementSerializer
    filterset_class = MeasurementFilter


class SymbologyViewSet(ViewSet):
    @action(methods=["GET"], detail=False)
    def icons(self, request):
        data = []
        used = set()

        for _, icon in SYMBOLS.items():
            if icon not in used:
                used.add(icon)
                path = static(f"icons/material/{icon}.png")
                url = request.build_absolute_uri(path)
                data.append({"name": icon, "url": url})

        return Response(data)
