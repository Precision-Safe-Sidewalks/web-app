from rest_framework_gis.serializers import GeoFeatureModelSerializer

from repairs.models import Measurement


class MeasurementSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for Measurements"""

    class Meta:
        model = Measurement
        geo_field = "coordinate"
        fields = ("id", "stage")
