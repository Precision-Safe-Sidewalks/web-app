import pyproj
from rest_framework import serializers

from lib.constants import CONVERT_METERS_TO_MILES
from repairs.models import Measurement, Project


class MeasurementSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    special_case = serializers.SerializerMethodField()
    hazard_size = serializers.SerializerMethodField()

    def get_longitude(self, obj):
        return obj.coordinate.x

    def get_latitude(self, obj):
        return obj.coordinate.y

    def get_special_case(self, obj):
        return obj.get_special_case_display()

    def get_hazard_size(self, obj):
        return obj.get_hazard_size_display()

    class Meta:
        model = Measurement
        fields = (
            "id",
            "object_id",
            "longitude",
            "latitude",
            "length",
            "width",
            "special_case",
            "hazard_size",
            "area",
            "geocoded_address",
            "note",
        )


class SquareFootPricingSheetSerializer(serializers.ModelSerializer):
    survey_date = serializers.SerializerMethodField()
    estimated_miles = serializers.SerializerMethodField()
    measurements = serializers.SerializerMethodField()

    def get_survey_date(self, obj):
        return obj.get_survey_date()

    def get_estimated_miles(self, obj):
        # FIXME: survey or production?
        distance = 0
        previous = None
        geod = pyproj.Geod(ellps="WGS84")

        for item in obj.get_survey_measurements().order_by("object_id"):
            current = item.coordinate

            if previous is not None:
                _, _, dist = geod.inv(previous.x, previous.y, current.x, current.y)
                distance += dist

            previous = current

        return distance * CONVERT_METERS_TO_MILES

    def get_measurements(self, obj):
        data = {}

        # FIXME: survey or production?
        for item in obj.get_survey_measurements():
            if item.survey_group not in data:
                data[item.survey_group] = []

            value = MeasurementSerializer(item).data
            data[item.survey_group].append(value)

        return data

    class Meta:
        model = Project
        fields = (
            "id",
            "customer",
            "name",
            "survey_date",
            "estimated_miles",
            "measurements",
        )
