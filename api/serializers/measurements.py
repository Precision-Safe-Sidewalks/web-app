from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from repairs.models import Measurement


class MeasurementSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for Measurements"""

    stage = serializers.SerializerMethodField()
    symbol = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    special_case = serializers.SerializerMethodField()
    hazard_size = serializers.SerializerMethodField()

    def get_stage(self, obj):
        return obj.get_stage_display()

    def get_symbol(self, obj):
        return obj.get_symbol()

    def get_color(self, obj):
        return obj.get_color()

    def get_special_case(self, obj):
        return obj.get_special_case_display()

    def get_hazard_size(self, obj):
        return obj.get_hazard_size_display()

    class Meta:
        model = Measurement
        geo_field = "coordinate"
        fields = (
            "id",
            "stage",
            "symbol",
            "color",
            "object_id",
            "special_case",
            "hazard_size",
            "length",
            "width",
            "measured_hazard_length",
            "curb_length",
            "h1",
            "h2",
            "area",
            "tech",
            "geocoded_address",
            "note",
            "slope",
            "inch_feet",
            "measured_at",
            "created_at",
        )
