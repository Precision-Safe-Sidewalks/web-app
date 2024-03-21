from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.utils.html import mark_safe
from rest_framework import serializers

from customers.models import Contact, Customer
from repairs.models import Project, ProjectManagementDashboardView

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
            "arcgis_username",
            "is_active",
            "is_admin",
            "phone_work",
            "phone_cell",
            "last_login",
        )


class DashboardTableSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    last_date = serializers.SerializerMethodField()
    last_synced_at = serializers.SerializerMethodField()
    hazards_remaining = serializers.SerializerMethodField()
    inch_feet_expected = serializers.SerializerMethodField()
    inch_feet_repaired = serializers.SerializerMethodField()
    inch_feet_remaining = serializers.SerializerMethodField()
    curb_length_expected = serializers.SerializerMethodField()
    curb_length_repaired = serializers.SerializerMethodField()
    curb_length_remaining = serializers.SerializerMethodField()
    square_feet_expected = serializers.SerializerMethodField()
    square_feet_repaired = serializers.SerializerMethodField()
    square_feet_remaining = serializers.SerializerMethodField()
    percent_complete_hazards = serializers.SerializerMethodField()
    percent_complete_inch_feet = serializers.SerializerMethodField()
    business_development_manager = serializers.CharField(source="bd_name")
    territory = serializers.CharField(source="territory_label")

    def get_customer(self, obj):
        href = reverse("customer-detail", kwargs={"pk": obj.customer_id})
        html = f'<a href="{href}">{obj.customer_name}</a>'
        return mark_safe(html)

    def get_name(self, obj):
        href = reverse("project-detail", kwargs={"pk": obj.project_id})
        html = f'<a href="{href}">{obj.name}</a>'
        return mark_safe(html)

    def get_status(self, obj):
        return Project.Status(obj.status).label

    def get_start_date(self, obj):
        return obj.start_date.strftime("%m/%d/%y") if obj.start_date else None

    def get_last_date(self, obj):
        return obj.last_date.strftime("%m/%d/%y") if obj.last_date else None

    def get_last_synced_at(self, obj):
        return obj.last_synced_at.strftime("%m/%d/%y") if obj.last_synced_at else None

    def get_hazards_remaining(self, obj):
        return obj.hazards_expected - obj.hazards_repaired

    def get_inch_feet_expected(self, obj):
        return round(obj.inch_feet_expected, 1)

    def get_inch_feet_repaired(self, obj):
        return round(obj.inch_feet_repaired, 1)

    def get_inch_feet_remaining(self, obj):
        return round(obj.inch_feet_expected - obj.inch_feet_repaired, 1)

    def get_curb_length_expected(self, obj):
        return round(obj.curb_length_expected, 1)

    def get_curb_length_repaired(self, obj):
        return round(obj.curb_length_repaired, 1)

    def get_curb_length_remaining(self, obj):
        return round(obj.curb_length_expected - obj.curb_length_repaired, 1)

    def get_square_feet_expected(self, obj):
        return round(obj.square_feet_expected, 1)

    def get_square_feet_repaired(self, obj):
        return round(obj.square_feet_repaired, 1)

    def get_square_feet_remaining(self, obj):
        return round(obj.square_feet_expected - obj.square_feet_repaired, 1)

    def get_percent_complete_hazards(self, obj):
        if obj.hazards_expected == 0:
            return "---"

        percent = obj.hazards_repaired / obj.hazards_expected
        return f"{round(100 * percent)}%"

    def get_percent_complete_inch_feet(self, obj):
        if obj.inch_feet_expected == 0:
            return "---"

        percent = obj.inch_feet_repaired / obj.inch_feet_expected
        return f"{round(100 * percent)}%"

    class Meta:
        model = ProjectManagementDashboardView
        fields = (
            "customer",
            "name",
            "business_development_manager",
            "status",
            "start_date",
            "last_date",
            "last_synced_at",
            "techs",
            "hazards_expected",
            "inch_feet_expected",
            "curb_length_expected",
            "square_feet_expected",
            "hazards_repaired",
            "inch_feet_repaired",
            "curb_length_repaired",
            "square_feet_repaired",
            "hazards_remaining",
            "inch_feet_remaining",
            "curb_length_remaining",
            "square_feet_remaining",
            "percent_complete_hazards",
            "percent_complete_inch_feet",
            "territory",
        )
