from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.utils.html import mark_safe
from rest_framework import serializers

from customers.models import Contact, Customer
from repairs.models import Project

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
        fields = ("name", "email", "phone_work", "phone_cell")


class CustomerTableSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    active_projects = serializers.SerializerMethodField()
    completed_projects = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    def get_name(self, obj):
        href = reverse("customer-detail", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.name}</a>'
        return mark_safe(html)

    def get_location(self, obj):
        return obj.short_address or ""

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
            "location",
            "active_projects",
            "completed_projects",
            "created",
        )


class ProjectTableSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    business_development_manager = serializers.SerializerMethodField()
    business_development_administrator = serializers.SerializerMethodField()
    territory = serializers.CharField(source="territory.label")
    primary_contact = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    def get_name(self, obj):
        href = reverse("project-detail", kwargs={"pk": obj.pk})
        html = f'<a href="{href}">{obj.name}</a>'
        return mark_safe(html)

    def get_status(self, obj):
        return obj.get_status_display()

    def get_business_development_manager(self, obj):
        if obj.business_development_manager:
            return obj.business_development_manager.full_name
        return None

    def get_business_development_administrator(self, obj):
        if obj.business_development_administrator:
            return obj.business_development_administrator.full_name
        return None

    def get_primary_contact(self, obj):
        contact = obj.primary_contact
        if contact:
            return contact.name
        return None

    def get_created(self, obj):
        return obj.created_at.strftime("%-m/%-d/%Y")

    class Meta:
        model = Project
        fields = (
            "name",
            "status",
            "business_development_manager",
            "business_development_administrator",
            "territory",
            "primary_contact",
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
