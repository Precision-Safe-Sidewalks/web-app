import uuid

import boto3
import pyproj
from django.db import models

from core.models.constants import States
from lib.constants import CONVERT_METERS_TO_MILES
from repairs.models.constants import HazardDensity, HazardTier, PanelSize
from repairs.models.projects import Project


class PricingSheet(models.Model):
    """Pricing sheet (inch foot/square foot) for a Project"""

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="pricing_sheet"
    )
    estimated_sidewalk_miles = models.FloatField(default=0)
    surveyor_speed = models.PositiveIntegerField(default=0)
    survey_hazards = models.IntegerField(
        choices=HazardTier.choices, default=HazardTier.ABOVE_LS
    )
    hazard_density = models.IntegerField(
        choices=HazardDensity.choices, default=HazardDensity.LOW
    )
    panel_size = models.IntegerField(
        choices=PanelSize.choices, default=PanelSize.FIVE_FOOT
    )
    distance_from_surveyor = models.PositiveIntegerField(default=0)
    distance_from_ops = models.PositiveIntegerField(default=0)
    commission_rate = models.FloatField(default=0)
    base_rate = models.FloatField(default=0, help_text="Base cost/square foot")
    number_of_technicians = models.PositiveIntegerField(default=0)

    def calculate_sidewalk_miles(self):
        """
        Calculate the sidewalk miles from the survey data. This is only 
        used for square foot pricing models.
        """
        distance = 0
        previous = None
        geod = pyproj.Geod(ellps="WGS84")

        for item in self.project.get_survey_measurements().order_by("object_id"):
            current = item.coordinate

            if previous is not None:
                _, _, dist = geod.inv(previous.x, previous.y, current.x, current.y)
                distance += dist

            previous = current

        miles = distance * CONVERT_METERS_TO_MILES
        self.estimated_sidewalk_miles = miles
        self.save()

    def get_contact(self):
        """Return the pricing sheet contact"""
        try:
            return self.contact
        except PricingSheetContact.DoesNotExist:
            return None


class PricingSheetContact(models.Model):
    """Pricing sheet contact (denormalized)"""

    class ContactType(models.TextChoices):
        """Pricing sheet contact type"""

        PRIMARY = ("PRIMARY", "Primary")
        SECONDARY = ("SECONDARY", "Secondary")
        OTHER = ("OTHER", "Other")

    pricing_sheet = models.OneToOneField(
        PricingSheet, on_delete=models.CASCADE, related_name="contact"
    )
    contact_type = models.CharField(
        max_length=25, choices=ContactType.choices, default=ContactType.PRIMARY
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(
        max_length=2, choices=States.choices, blank=True, null=True
    )
    zip_code = models.CharField(max_length=6, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.address = self.format_address()
        super().save(*args, **kwargs)

    def format_address(self):
        """Return the formatted address as a string"""
        required = ("street", "city", "state", "zip_code")
        has_required = all((getattr(self, k, None) for k in required))

        if not has_required:
            return None

        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


class PricingSheetRequest(models.Model):
    """Pricing sheet generation/download request"""

    pricing_sheet = models.ForeignKey(
        PricingSheet, on_delete=models.CASCADE, related_name="requests"
    )
    request_id = models.UUIDField(default=uuid.uuid4, editable=False)
    s3_bucket = models.CharField(max_length=255, blank=True, null=True)
    s3_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_download_url(self):
        """Return the pre-signed S3 URL"""
        if not (self.s3_bucket and self.s3_key):
            return None

        params = {"Bucket": self.s3_bucket, "Key": self.s3_key}
        expires_in = 10 * 60  # 10 minutes

        s3 = boto3.client("s3")
        return s3.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=expires_in
        )
