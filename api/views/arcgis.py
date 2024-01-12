from rest_framework.viewsets import ModelViewSet

from api.serializers.arcgis import ArcGISItemSerializer
from third_party.arcgis.models import ArcGISItem


class ArcGISItemViewSet(ModelViewSet):
    """ArcGIS Item API view set"""

    queryset = ArcGISItem.objects.order_by("id")
    serializer_class = ArcGISItemSerializer
    # filterset_class = ArcGISItemFilter
