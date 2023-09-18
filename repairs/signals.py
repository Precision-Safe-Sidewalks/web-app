from django.db.models.signals import post_save
from django.dispatch import receiver

from repairs.models import Instruction, InstructionChecklist, Project
from repairs.models.constants import Stage


@receiver(post_save, sender=Project)
def initialize_instructions(sender, instance, created, **kwargs):
    """Initialize the survey/project instructions"""

    if created:
        Instruction.objects.create(project=instance, stage=Stage.SURVEY)
        pi = Instruction.objects.create(project=instance, stage=Stage.PRODUCTION)
        InstructionChecklist.create_for_instruction(pi)
