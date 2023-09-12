from django.contrib.auth import get_user_model
from django.db import models

from repairs.models.constants import Stage
from repairs.models.projects import Project

User = get_user_model()


class Instruction(models.Model):
    """Survey/Project instructions set"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="instructions"
    )
    stage = models.CharField(max_length=25, choices=Stage.choices)
    surveyed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="instructions_surveyed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: survey needed by (project or instruction level)
    # TODO: survey method (SI only)
    # TODO: required number of images + sizes
    # TODO: cuts (PI only)
    # TODO: bidboss production, NTE/no survey, only pins, GD streets link (PI only)


class InstructionSpecification(models.Model):
    """Survey/Project instructions specifications set"""

    class SpecificationType(models.TextChoices):
        """Specification type choices"""

        HAZARD = ("H", "Hazard")
        SPECIAL_CASE = ("SC", "Special case")
        DR = ("DR", "D&R specification")

    class PricingModel(models.TextChoices):
        """Pricing model type choices"""

        STANDARD = ("S", "Standard")
        SQFT = ("SQFT", "Square foot")

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name="specifications"
    )
    specification_type = models.CharField(
        max_length=10, choices=SpecificationType.choices
    )
    specification = models.CharField(max_length=10)
    pricing_model = models.CharField(
        max_length=10, choices=PricingModel.choices, blank=True, null=True
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("instruction", "specification_type", "specification")


class InstructionNote(models.Model):
    """Survey/Project instructions note set"""

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name="notes"
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)