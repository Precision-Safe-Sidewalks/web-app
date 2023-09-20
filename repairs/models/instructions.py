from django.contrib.auth import get_user_model
from django.db import models

from customers.models import Contact
from repairs.models.constants import ReferenceImageMethod, Stage
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
    needed_by = models.DateField(blank=True, null=True)
    needed_asap = models.BooleanField(default=False)
    details = models.TextField(blank=True, null=True)
    survey_method = models.CharField(max_length=255, blank=True, null=True)
    reference_images_method = models.IntegerField(
        choices=ReferenceImageMethod.choices, default=ReferenceImageMethod.EVERYTHING
    )
    reference_images_required = models.PositiveIntegerField(default=0)
    reference_images_sizes = models.CharField(max_length=50, blank=True, null=True)
    reference_images_curbs = models.BooleanField(default=False)
    po_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: cuts (PI only)
    # TODO: bidboss production, NTE/no survey, only pins, GD streets link (PI only)

    def get_needed_by_display(self):
        """Return the needed_by date for display"""
        if self.needed_by:
            return self.needed_by.strftime("%m/%d/%Y")
        return None

    def get_primary_contact_notes(self):
        """Return any notes for the primary contact"""
        return self.contact_notes.filter(contact=self.project.primary_contact).order_by(
            "created_at"
        )

    def get_secondary_contact_notes(self):
        """Return any notes for the secondary contact"""
        return self.contact_notes.filter(
            contact=self.project.secondary_contact
        ).order_by("created_at")

    def get_notes(self):
        """Return the notes in chronological order"""
        return self.notes.order_by("created_at")

    def get_survey_date(self):
        """Return the survey date (from the survey measurements)"""
        measurement = self.project.measurements.filter(stage=Stage.SURVEY).order_by("measured_at").first()
        return measurement.measured_at if measurement else None


class InstructionContactNote(models.Model):
    """Survey/Project instructions contact note"""

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name="contact_notes"
    )
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InstructionSpecification(models.Model):
    """Survey/Project instructions specifications set"""

    class SpecificationType(models.TextChoices):
        """Specification type choices"""

        HAZARD = ("H", "Hazard")
        SPECIAL_CASE = ("SC", "Special case")
        DR = ("DR", "D&R specification")

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name="specifications"
    )
    specification_type = models.CharField(
        max_length=10, choices=SpecificationType.choices
    )
    specification = models.CharField(max_length=10)
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
