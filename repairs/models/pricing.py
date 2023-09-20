from django.db import models

from repairs.models.constants import HazardDensity, HazardTier, PanelSize
from repairs.models.projects import Project


class PricingSheet(models.Model):
    """Pricing sheet (inch foot/square foot) for a Project"""

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="pricing_sheet"
    )
    estimated_sidewalk_miles = models.PositiveIntegerField(default=0)
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
