from rest_framework import serializers

from api.serializers.core import TerritorySerializer
from api.serializers.customers import CustomerSerializer
from repairs.models import Measurement, PricingSheet, PricingSheetContact, Project


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
            "curb_length",
            "measured_hazard_length",
            "inch_feet",
            "area",
            "geocoded_address",
            "note",
        )


class PricingSheetContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingSheetContact
        fields = "__all__"


class PricingSheetDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingSheet
        fields = "__all__"


class PricingSheetSerializer(serializers.ModelSerializer):
    survey_date = serializers.SerializerMethodField()
    measurements = serializers.SerializerMethodField()
    customer = CustomerSerializer()
    territory = TerritorySerializer()
    pricing_model = serializers.SerializerMethodField()
    pricing = PricingSheetDataSerializer(source="pricing_sheet")
    contact = serializers.SerializerMethodField()

    def get_survey_date(self, obj):
        return obj.get_survey_date()

    def get_pricing_model(self, obj):
        return obj.get_pricing_model_display()

    def get_measurements(self, obj):
        data = {}

        for item in obj.get_survey_measurements():
            if item.survey_group not in data:
                data[item.survey_group] = []

            value = MeasurementSerializer(item).data
            data[item.survey_group].append(value)

        return data

    def get_contact(self, obj):
        contact = PricingSheetContact.objects.filter(pricing_sheet__project=obj).first()

        if contact:
            return PricingSheetContactSerializer(contact).data

        return None

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "customer",
            "territory",
            "pricing",
            "contact",
            "survey_date",
            "pricing_model",
            "measurements",
        )
