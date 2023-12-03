from rest_framework import serializers

from api.serializers.accounts import UserSerializer
from api.serializers.core import TerritorySerializer
from api.serializers.customers import CustomerSerializer
from repairs.models import Measurement, PricingSheet, PricingSheetContact, Project
from repairs.models.constants import Stage


class MeasurementSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    special_case = serializers.SerializerMethodField()
    hazard_size = serializers.SerializerMethodField()
    tech_initials = serializers.SerializerMethodField()
    work_date = serializers.SerializerMethodField()

    def get_longitude(self, obj):
        return obj.coordinate.x

    def get_latitude(self, obj):
        return obj.coordinate.y

    def get_special_case(self, obj):
        return obj.get_special_case_display()

    def get_hazard_size(self, obj):
        return obj.get_hazard_size_display()

    def get_tech_initials(self, obj):
        if obj.tech:
            return (obj.tech[0] + obj.tech[2]).upper()
        return None

    def get_work_date(self, obj):
        return obj.measured_at.date()

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
            "h1",
            "h2",
            "area",
            "geocoded_address",
            "note",
            "tech",
            "tech_initials",
            "work_date",
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
    business_development_manager = UserSerializer()
    surveyor = serializers.SerializerMethodField()

    def get_survey_date(self, obj):
        return obj.get_survey_date()

    def get_pricing_model(self, obj):
        return obj.get_pricing_model_display()

    def get_measurements(self, obj):
        data = []
        index = {}

        for item in obj.get_survey_measurements():
            if item.survey_group not in index:
                index[item.survey_group] = len(data)
                data.append({"name": item.survey_group, "data": []})

            group = index[item.survey_group]
            value = MeasurementSerializer(item).data
            data[group]["data"].append(value)

        return data

    def get_contact(self, obj):
        contact = PricingSheetContact.objects.filter(pricing_sheet__project=obj).first()

        if contact:
            return PricingSheetContactSerializer(contact).data

        return None

    def get_surveyor(self, obj):
        instructions = obj.instructions.filter(stage=Stage.SURVEY).first()

        if instructions and instructions.surveyed_by:
            return UserSerializer(instructions.surveyed_by).data

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
            "business_development_manager",
            "surveyor",
            "measurements",
        )


class PricingSheetCompleteSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    s3_bucket = serializers.CharField(max_length=50)
    s3_key = serializers.CharField(max_length=255)


class ProjectSummarySerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    territory = TerritorySerializer()
    business_development_manager = UserSerializer()
    pricing_model = serializers.SerializerMethodField()
    pricing = PricingSheetDataSerializer(source="pricing_sheet")
    contact = serializers.SerializerMethodField()
    survey_date = serializers.SerializerMethodField()
    surveyor = serializers.SerializerMethodField()
    hazards = serializers.SerializerMethodField()
    measurements = serializers.SerializerMethodField()

    def get_pricing_model(self, obj):
        return obj.get_pricing_model_display()

    def get_survey_date(self, obj):
        return obj.get_survey_date()

    def get_contact(self, obj):
        contact = PricingSheetContact.objects.filter(pricing_sheet__project=obj).first()

        if contact:
            return PricingSheetContactSerializer(contact).data

        return None

    def get_surveyor(self, obj):
        instructions = obj.instructions.filter(stage=Stage.SURVEY).first()

        if instructions and instructions.surveyed_by:
            return UserSerializer(instructions.surveyed_by).data

        return None

    def get_hazards(self, obj):
        instructions = obj.instructions.filter(stage=Stage.PRODUCTION).first()
        hazards = {"count": 0, "inch_feet": 0, "square_feet": 0, "linear_feet_curb": 0}

        if instructions:
            hazards["linear_feet_curb"] = instructions.linear_feet_curb

            for _, values in instructions.hazards.items():
                hazards["count"] += values.get("count", 0)
                hazards["inch_feet"] += values.get("inch_feet", 0)
                hazards["square_feet"] += values.get("square_feet", 0)

        return hazards

    def get_measurements(self, obj):
        data = []
        index = {}

        for item in obj.get_production_measurements().order_by("measured_at"):
            work_date = item.measured_at.date()

            if work_date not in index:
                index[work_date] = len(data)
                data.append({"name": str(work_date), "data": []})

            group = index[work_date]
            value = MeasurementSerializer(item).data
            data[group]["data"].append(value)

        # Sort the values for each work date by tech/object_id
        for i, items in enumerate(data):
            values = items["data"]
            values.sort(key=lambda r: (r["tech"], r["object_id"]))
            data[i]["data"] = values

        return data

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "po_number",
            "pricing_model",
            "territory",
            "customer",
            "business_development_manager",
            "surveyor",
            "survey_date",
            "pricing",
            "contact",
            "hazards",
            "measurements",
        )


class ProjectSummaryCompleteSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    s3_bucket = serializers.CharField(max_length=50)
    s3_key = serializers.CharField(max_length=255)
