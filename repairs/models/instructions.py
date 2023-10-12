from django.contrib.auth import get_user_model
from django.db import models

from customers.models import Contact
from repairs.models.constants import (
    ContactMethod,
    Cut,
    Hazard,
    ProjectSpecification,
    ReferenceImageMethod,
    Stage,
)
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
    cut = models.IntegerField(choices=Cut.choices, default=Cut.ONE_EIGHT)
    contact_method = models.IntegerField(
        choices=ContactMethod.choices, default=ContactMethod.CALL
    )
    hazards = models.JSONField(default=dict, help_text="Aggregated hazard counts")
    linear_feet_curb = models.FloatField(
        default=0, help_text="Approved PI curb linear feet"
    )
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_default_hazards(self):
        """Return the default hazards from the survey measurements"""

        if self.stage != Stage.PRODUCTION:
            return {}

        hazards = {}
        queryset = self.project.measurements.filter(stage=Stage.SURVEY)

        for value, name in Hazard.choices:
            size = Hazard.get_size(value)
            data = queryset.filter(size=size)

            count = data.count()
            sqft = sum([m.length * m.width for m in data if m.length and m.width])
            inft = sum([m.inch_feet for m in data if m.inch_feet])

            hazards[value] = {"count": count, "square_feet": sqft, "inch_feet": inft}

        return hazards

    def get_needed_by_display(self):
        """Return the needed_by date for display"""
        if self.needed_by:
            return self.needed_by.strftime("%m/%d/%Y")
        return None

    def get_cut_display(self):
        """Return the cut for display"""
        if self.cut:
            return Cut(self.cut).label
        return None

    def get_contact_method_display(self):
        """Return the contact method for display"""
        if self.contact_method:
            return ContactMethod(self.contact_method).label
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
        measurement = (
            self.project.measurements.filter(stage=Stage.SURVEY)
            .order_by("measured_at")
            .first()
        )
        return measurement.measured_at.strftime("%-m/%-d/%Y") if measurement else None

    def get_checklist(self):
        """Return the checklist in order"""
        return self.checklist.order_by("question__order", "question__suborder")

    def get_checklist_visible(self):
        """Return True if the checklist should be visible"""
        return self.specifications.filter(
            specification_type=InstructionSpecification.SpecificationType.PROJECT,
            specification=ProjectSpecification.NTE,
        ).exists()


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
        PROJECT = ("P", "Project specification")

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


class InstructionChecklistQuestion(models.Model):
    """Project instruction checklist question"""

    order = models.PositiveIntegerField()
    suborder = models.IntegerField(default=-1)
    question = models.CharField(max_length=255)


class InstructionChecklist(models.Model):
    """Project instruction checklist"""

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name="checklist"
    )
    question = models.ForeignKey(InstructionChecklistQuestion, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
