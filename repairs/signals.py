from django.db.models.signals import post_save
from django.dispatch import receiver

from repairs.models import (
    Instruction,
    InstructionChecklist,
    InstructionChecklistQuestion,
    PricingSheet,
    Project,
)
from repairs.models.constants import Stage


@receiver(post_save, sender=Project)
def initialize_instructions(sender, instance, created, **kwargs):
    """Initialize the survey/project instructions"""

    Instruction.objects.get_or_create(project=instance, stage=Stage.SURVEY)
    pi, _ = Instruction.objects.get_or_create(project=instance, stage=Stage.PRODUCTION)

    for question in InstructionChecklistQuestion.objects.all():
        InstructionChecklist.objects.get_or_create(instruction=pi, question=question)

    PricingSheet.objects.get_or_create(project=instance)
