from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Coalesce

from customers.models import Contact
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
    needed_by = models.DateField(blank=True, null=True)
    needed_asap = models.BooleanField(default=False)
    details = models.TextField(blank=True, null=True)
    survey_method = models.CharField(max_length=255, blank=True, null=True)
    survey_method_note = models.CharField(max_length=255, blank=True, null=True)
    survey_date = models.DateField(blank=True, null=True)
    reference_images_required = models.PositiveIntegerField(default=0)
    reference_images_sizes = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def get_checklist(self):
        """Return the ordered checklist"""
        return self.checklist.annotate(
            suborder=Coalesce("question__suborder", -1)
        ).order_by("question__order", "suborder")


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
        PRODUCTION = ("P", "Producton")

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


class InstructionChecklistQuestion(models.Model):
    """Project instructions check list questions"""

    order = models.PositiveIntegerField()
    suborder = models.PositiveIntegerField(blank=True, null=True)
    question = models.CharField(max_length=255)

    def __str__(self):
        if self.suborder:
            return f"- {self.question}"
        return f"{self.order}. {self.question}"


class InstructionChecklist(models.Model):
    """Project instructions checklist"""

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name="checklist"
    )
    question = models.ForeignKey(InstructionChecklistQuestion, on_delete=models.CASCADE)
    response = models.TextField(blank=True, null=True)

    @classmethod
    def create_for_instruction(cls, instruction):
        """Initialize a checklist for an instruction"""
        for question in InstructionChecklistQuestion.objects.all():
            cls.objects.create(instruction=instruction, question=question)
