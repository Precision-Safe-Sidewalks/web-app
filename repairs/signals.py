from django.db.models.signals import post_save
from django.dispatch import receiver

from customers.models import Customer
from repairs.models import (
    Instruction,
    InstructionChecklist,
    InstructionChecklistQuestion,
    PricingSheet,
    PricingSheetRequest,
    Project,
    ProjectSummaryRequest,
)
from repairs.models.constants import Stage
from utils.aws import invoke_lambda_function


@receiver(post_save, sender=Project)
def initialize_instructions(sender, instance, created, **kwargs):
    """Initialize the survey/project instructions"""

    Instruction.objects.get_or_create(project=instance, stage=Stage.SURVEY)
    pi, _ = Instruction.objects.get_or_create(project=instance, stage=Stage.PRODUCTION)

    for question in InstructionChecklistQuestion.objects.all():
        InstructionChecklist.objects.get_or_create(instruction=pi, question=question)

    PricingSheet.objects.get_or_create(project=instance)


@receiver(post_save, sender=PricingSheetRequest)
def generate_pricing_sheet(sender, instance, created, **kwargs):
    """Trigger the pricing sheet generation Lambda function"""

    if created:
        payload = {
            "request_id": instance.request_id,
            "project_id": instance.pricing_sheet.project_id,
        }
        invoke_lambda_function("pricing_sheet", payload=payload)


@receiver(post_save, sender=ProjectSummaryRequest)
def generate_project_summary(sender, instance, created, **kwargs):
    """Trigger the project summary generation Lambda function"""

    if created:
        payload = {
            "request_id": instance.request_id,
            "project_id": instance.project_id,
        }
        invoke_lambda_function("project_summary", payload=payload)


@receiver(post_save, sender=Customer)
def update_project_bdm(sender, instance, **kwargs):
    """Update the BDM for all customer projects"""
    for project in instance.projects.all():
        project.business_development_manager = instance.business_development_manager
        project.save()
