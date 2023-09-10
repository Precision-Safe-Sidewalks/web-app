import json

import boto3
from django.conf import settings
from django.contrib.gis.db.models.fields import PointField
from django.db import models, transaction

from repairs.models.constants import QuickDescription, SpecialCase, Stage
from repairs.models.projects import Project
from repairs.parsers import ProductionMeasurement, SurveyMeasurement


class Measurement(models.Model):
    """Survey measurement GIS data and metadata"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="measurements"
    )
    stage = models.CharField(max_length=25, choices=Stage.choices)
    object_id = models.IntegerField()
    global_id = models.UUIDField()
    coordinate = PointField()
    length = models.FloatField(blank=True, null=True)
    width = models.FloatField(blank=True, null=True)
    special_case = models.CharField(
        max_length=10, choices=SpecialCase.choices, blank=True, null=True
    )
    quick_description = models.CharField(
        max_length=10, choices=QuickDescription.choices, blank=True, null=True
    )
    h1 = models.FloatField(blank=True, null=True)
    h2 = models.FloatField(blank=True, null=True)
    linear_feet = models.FloatField(blank=True, null=True)
    inch_feet = models.FloatField(blank=True, null=True)
    slope = models.CharField(max_length=10, blank=True, null=True)
    curb_length = models.FloatField(blank=True, null=True)
    survey_address = models.CharField(max_length=255, blank=True, null=True)
    surveyor = models.CharField(max_length=100)
    note = models.TextField(blank=True, null=True)
    geocoded_address = models.CharField(max_length=255, blank=True, null=True)
    measured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        (x, y) = self.coordinate.coords
        return f"{self.project.name} - {self.object_id} - ({x}, {y})"

    @staticmethod
    def import_from_csv(file_obj, project, stage):
        """Import the Measurements from CSV (replaces any existing)"""
        file_obj.seek(0)

        if stage == Stage.SURVEY:
            parser_cls = SurveyMeasurement
        else:
            parser_cls = ProductionMeasurement

        with transaction.atomic():
            Measurement.objects.filter(project=project, stage=stage).delete()

            for data in parser_cls.from_csv(file_obj):
                kwargs = data.model_dump()
                Measurement.objects.create(project=project, stage=stage, **kwargs)

        # Trigger the Lambda function to reverse geocode the addresses
        # based on the coordinates by adding the (project_id, stage) to
        # the SQS queue
        queue_url = settings.MEASUREMENT_GEOCODING_QUEUE_URL

        if queue_url:
            payload = json.dumps({"project_id": project.pk, "stage": stage})
            sqs = boto3.client("sqs")
            sqs.send_message(QueueUrl=queue_url, MessageBody=payload)

        return Measurement.objects.filter(project=project, stage=stage)


class MeasurementImage(models.Model):
    """Reference image for a Measurement"""

    measurement = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, related_name="images"
    )
    url = models.URLField()
    captured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
