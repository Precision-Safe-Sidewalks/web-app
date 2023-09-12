from django.dispatch import receiver
from django.db.models.signals import post_save

from repairs.models import Project, Instruction
from repairs.models.constants import Stage


@receiver(post_save, sender=Project)
def initialize_instructions(sender, instance, created, **kwargs):
    """Initialize the survey/project instructions"""

    if created:
        Instruction.objects.create(project=instance, stage=Stage.SURVEY)
        Instruction.objects.create(project=instance, stage=Stage.PRODUCTION)
