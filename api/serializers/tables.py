import functools

from django.contrib.auth import get_user_model
from django.db.models import Max, Min, F, Sum, Count
from django.db.models.functions import Round
from django.shortcuts import reverse
from django.utils.html import mark_safe
from rest_framework import serializers

from api.serializers.customers import SimpleCustomerSerializer
from api.serializers.users import SimpleUserSerializer
from api.serializers.core import SimpleTerritorySerializer
from customers.models import Contact, Customer
from repairs.models import Project
from repairs.models.constants import Stage

User = get_user_model()


class ContactTableSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    phone_work = serializers.SerializerMethodField()
    phone_cell = serializers.SerializerMethodField()

    def get_name(self, obj):
        href = reverse("contact-update", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.name}</a>'
        return mark_safe(html)

    def get_phone_work(self, obj):
        number = obj.get_work_phone()
        return str(number) if number else None

    def get_phone_cell(self, obj):
        number = obj.get_cell_phone()
        return str(number) if number else None

    class Meta:
        model = Contact
        fields = ("name", "title", "email", "phone_work", "phone_cell")


class CustomerTableSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    business_development_manager = serializers.SerializerMethodField()
    territory = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    segment = serializers.SerializerMethodField()
    active_projects = serializers.SerializerMethodField()
    completed_projects = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    def get_name(self, obj):
        href = reverse("customer-detail", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.name}</a>'
        return mark_safe(html)

    def get_business_development_manager(self, obj):
        if obj.business_development_manager:
            return obj.business_development_manager.full_name
        return None

    def get_territory(self, obj):
        if obj.territory:
            return obj.territory.label
        return None

    def get_location(self, obj):
        return obj.short_address

    def get_segment(self, obj):
        return obj.get_segment_display()

    def get_active_projects(self, obj):
        return obj.active_projects.count()

    def get_completed_projects(self, obj):
        return obj.completed_projects.count()

    def get_created(self, obj):
        return obj.created_at.strftime("%-m/%-d/%Y")

    class Meta:
        model = Customer
        fields = (
            "name",
            "business_development_manager",
            "territory",
            "location",
            "segment",
            "active_projects",
            "completed_projects",
            "created",
        )


class ProjectTableSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    business_development_manager = serializers.SerializerMethodField()
    segment = serializers.SerializerMethodField()
    territory = serializers.CharField(source="territory.label")
    created = serializers.SerializerMethodField()

    def get_customer(self, obj):
        href = reverse("customer-detail", kwargs={"pk": obj.customer_id})
        html = f'<a href="{href}">{obj.customer.name}</a>'
        return mark_safe(html)

    def get_name(self, obj):
        href = reverse("project-detail", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.name}</a>'
        return mark_safe(html)

    def get_stage(self, obj):
        return obj.get_status_display()

    def get_business_development_manager(self, obj):
        if obj.business_development_manager:
            return obj.business_development_manager.full_name
        return None

    def get_segment(self, obj):
        return obj.customer.get_segment_display()

    def get_created(self, obj):
        return obj.created_at.strftime("%-m/%-d/%Y")

    class Meta:
        model = Project
        fields = (
            "customer",
            "name",
            "business_development_manager",
            "territory",
            "stage",
            "segment",
            "created",
        )


class UserTableSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    phone_work = serializers.SerializerMethodField()
    phone_cell = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()

    def get_name(self, obj):
        href = reverse("user-update", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.full_name}</a>'
        return mark_safe(html)

    def get_email(self, obj):
        href = reverse("user-update", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.email}</a>'
        return mark_safe(html)

    def get_is_active(self, obj):
        if obj.is_active:
            html = '<span class="icon icon--success">check_circle</span>'
        else:
            html = '<span class="icon icon--error">cancel</span>'

        return mark_safe(html)

    def get_is_admin(self, obj):
        if obj.is_superuser:
            html = '<span class="icon icon--success">check_circle</span>'
        else:
            html = '<span class="icon icon--error">cancel</span>'

        return mark_safe(html)

    def get_phone_work(self, obj):
        phone = obj.get_work_phone()
        return str(phone) if phone else None

    def get_phone_cell(self, obj):
        phone = obj.get_cell_phone()
        return str(phone) if phone else None

    def get_last_login(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%-m/%-d/%Y %-I:%M %p")
        return None

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "is_active",
            "is_admin",
            "phone_work",
            "phone_cell",
            "last_login",
        )


class DashboardTableSerializer(serializers.ModelSerializer):
    customer = SimpleCustomerSerializer()
    start_date = serializers.SerializerMethodField()
    last_date = serializers.SerializerMethodField()
    techs = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    hazards_expected = serializers.SerializerMethodField()
    hazards_repaired = serializers.SerializerMethodField()
    inch_feet_expected = serializers.SerializerMethodField()
    inch_feet_repaired = serializers.SerializerMethodField()
    square_feet_expected = serializers.SerializerMethodField()
    square_feet_repaired = serializers.SerializerMethodField()
    curb_length_expected = serializers.SerializerMethodField()
    curb_length_repaired = serializers.SerializerMethodField()
    business_development_manager = SimpleUserSerializer()
    territory = SimpleTerritorySerializer()

    @functools.cache
    def get_aggregated_data(self, obj):
        return obj.measurements.filter(stage=Stage.PRODUCTION).aggregate(
            start_date=Min("measured_at"),
            last_date=Max("measured_at"),
            inch_feet=Round(Sum("inch_feet", default=0), 2),
            square_feet=Round(Sum("area", default=0), 2),
            curb_length=Round(Sum("curb_length", default=0), 2),
            count=Count("id"),
        )

    @functools.cache
    def get_expected_values(self, obj):
        """Return the expected values (inch feet, square feet, hazard count)"""
        values = {"count": 0, "inch_feet": 0, "square_feet": 0, "curb_length": 0}
        instruction = obj.instructions.filter(stage=Stage.PRODUCTION).first()

        if not instruction:
            return values

        for _, entry in instruction.hazards.items():
            for key in values:
                values[key] += entry.get(key, 0)

        values["inch_feet"] = round(values["inch_feet"], 2)
        values["square_feet"] = round(values["square_feet"], 2)

        return values

    def get_start_date(self, obj):
        return self.get_aggregated_data(obj)["start_date"]

    def get_last_date(self, obj):
        return self.get_aggregated_data(obj)["last_date"]

    def get_techs(self, obj):
        queryset = (
            obj.measurements.filter(stage=Stage.PRODUCTION, tech__isnull=False)
            .order_by("tech")
            .values_list("tech", flat=True)
            .distinct()
        )

        techs = []

        for username in queryset:
            tech = {"username": username, "initials": None}

            if len(username) >= 3:
                tech["initials"] = f"{username[0]}{username[2]}".upper()

            techs.append(tech)

        return techs

    def get_status(self, obj):
        return obj.get_status_display()

    def get_hazards_expected(self, obj):
        return self.get_expected_values(obj)["count"]

    def get_hazards_repaired(self, obj):
        return self.get_aggregated_data(obj)["count"]

    def get_inch_feet_expected(self, obj):
        return self.get_expected_values(obj)["inch_feet"]

    def get_inch_feet_repaired(self, obj):
        return self.get_aggregated_data(obj)["inch_feet"]

    def get_square_feet_expected(self, obj):
        return self.get_expected_values(obj)["square_feet"]

    def get_square_feet_repaired(self, obj):
        return self.get_aggregated_data(obj)["square_feet"]

    def get_curb_length_expected(self, obj):
        return self.get_expected_values(obj)["curb_length"]

    def get_curb_length_repaired(self, obj):
        return self.get_aggregated_data(obj)["curb_length"]

    class Meta:
        model = Project
        fields = (
            "id",
            "customer",
            "name",
            "status",
            "start_date",
            "last_date",
            "techs",
            "hazards_expected",
            "hazards_repaired",
            "inch_feet_expected",
            "inch_feet_repaired",
            "square_feet_expected",
            "square_feet_repaired",
            "curb_length_expected",
            "curb_length_repaired",
            "business_development_manager",
            "territory",
        )
