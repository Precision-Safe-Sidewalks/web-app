import csv

from django.contrib.gis.db.models.fields import PointField
from django.db import models, transaction

from repairs.models.constants import (
    SYMBOL_COLORS,
    SYMBOLS,
    QuickDescription,
    SpecialCase,
    Stage,
)
from repairs.models.projects import Project
from repairs.parsers import get_parser_class
from utils.aws import invoke_lambda_function


class Measurement(models.Model):
    """Survey measurement GIS data and metadata"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="measurements"
    )
    stage = models.CharField(max_length=25, choices=Stage.choices)
    coordinate = PointField()
    object_id = models.IntegerField()
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    curb_length = models.FloatField(default=0)
    measured_hazard_length = models.FloatField(default=0)
    h1 = models.FloatField(default=0)
    h2 = models.FloatField(default=0)
    hazard_size = models.CharField(
        max_length=10, choices=QuickDescription.choices, blank=True, null=True
    )
    special_case = models.CharField(
        max_length=10, choices=SpecialCase.choices, blank=True, null=True
    )
    geocoded_address = models.CharField(max_length=255, blank=True, null=True)
    survey_address = models.CharField(max_length=255, blank=True, null=True)
    survey_group = models.CharField(max_length=100, blank=True, null=True)
    tech = models.CharField(max_length=255, blank=True, null=True)
    area = models.FloatField(
        default=0, help_text="Length x Width (square feet)"
    )  # TODO: calculate and save
    note = models.TextField(blank=True, null=True)
    slope = models.CharField(max_length=10, blank=True, null=True)
    inch_feet = models.FloatField(default=0)
    measured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        (x, y) = self.coordinate.coords
        return f"{self.project.name} - {self.object_id} - ({x}, {y})"

    def save(self, *args, **kwargs):
        if self.special_case == SpecialCase.CURB:
            self.measured_hazard_length = self.curb_length * 12

            if self.stage == Stage.PRODUCTION:
                self.length = 0.5

        super().save(*args, **kwargs)

    @staticmethod
    def import_from_csv(file_obj, project, stage):
        """Import the Measurements from CSV (replaces any existing)"""
        file_obj.seek(0)
        parser_cls = get_parser_class(stage)

        with transaction.atomic():
            Measurement.objects.filter(project=project, stage=stage).delete()

            for data in parser_cls.from_csv(file_obj):
                kwargs = data.model_dump(exclude_none=True, exclude={"long", "lat"})
                Measurement.objects.create(project=project, stage=stage, **kwargs)

        # Trigger the Lambda function to reverse geocode the addresses
        # based on the coordinates by adding the (project_id, stage) to
        # the SQS queue
        payload = {"project_id": project.pk, "stage": stage}
        invoke_lambda_function("geocoding", payload)

        return Measurement.objects.filter(project=project, stage=stage)

    @staticmethod
    def export_to_csv(file_obj, project, stage):
        """Export the Measurements to CSV"""
        parser_cls = get_parser_class(stage)
        columns = list(parser_cls.model_fields)
        columns.remove("coordinate")
        aliases = {key: field.alias for key, field in parser_cls.model_fields.items()}

        measurements = list(
            Measurement.objects.filter(project=project, stage=stage)
            .annotate(
                long=models.ExpressionWrapper(
                    models.Func("coordinate", function="ST_X"),
                    output_field=models.FloatField(),
                )
            )
            .annotate(
                lat=models.ExpressionWrapper(
                    models.Func("coordinate", function="ST_Y"),
                    output_field=models.FloatField(),
                )
            )
            .order_by("object_id")
            .values(*columns)
        )

        encoders = {
            "special_case": SpecialCase,
            "hazard_size": QuickDescription,
        }

        for i, measurement in enumerate(measurements):
            for column, encoding in encoders.items():
                value = measurement[column]

                if value and column in measurement:
                    measurement[column] = encoding(value).label

            ordered = {}

            for column in parser_cls.order():
                value = measurement.get(column)
                alias = aliases.get(column, column)
                ordered[alias] = value

            measurements[i] = ordered

        fieldnames = [aliases.get(key, key) for key in parser_cls.order()]
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(measurements)
        file_obj.seek(0)

    def get_symbol(self):
        """Return the symbol to represent the measurement"""
        return SYMBOLS.get(self.special_case, "location_on")

    def get_color(self):
        """Return the color to represent the measurement"""
        if color := SYMBOL_COLORS.get(self.special_case):
            return color

        if color := SYMBOL_COLORS.get(self.hazard_size):
            return color

        return "black"


class MeasurementImage(models.Model):
    """Reference image for a Measurement"""

    measurement = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, related_name="images"
    )
    url = models.URLField()
    captured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
