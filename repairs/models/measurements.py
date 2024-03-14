import csv
from datetime import timedelta

from dateutil.parser import parse as parse_dt
from django.contrib.gis.db.models.fields import PointField
from django.db import connection, models, transaction

from repairs.models.constants import (
    SYMBOL_COLORS,
    SYMBOLS,
    PricingModel,
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

        # For square foot pricing models, calculate the estimated sidewalk
        # miles from the measurements.
        if project.pricing_model == PricingModel.SQUARE_FOOT:
            project.pricing_sheet.calculate_sidewalk_miles()

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

    @classmethod
    def get_tech_production(cls, start_date, end_date, techs=[]):
        """Get the tech production in the date range"""
        if isinstance(start_date, str):
            start_date = parse_dt(start_date).date()

        if isinstance(end_date, str):
            end_date = parse_dt(end_date).date()

        days = (end_date - start_date).days
        dates = [start_date + timedelta(days=d) for d in range(days)]
        params = {"start_date": start_date, "end_date": end_date}

        columns = [
            "tech",
            "COALESCE(COUNT(id), 0) AS total_records",
            "COALESCE(COUNT(DISTINCT(DATE(measured_at))), 0) AS total_days",
            "COALESCE(SUM(inch_feet), 0) AS total_inch_feet",
        ]

        for i, date in enumerate(dates):
            column = f"SUM(inch_feet) FILTER (WHERE DATE(measured_at) = '{date}') AS \"{date}\""
            columns.append(column)

        if techs:
            techs = ", ".join([f"'{tech}'" for tech in techs])
            filter_techs = f"AND tech IN ({techs})"
        else:
            filter_techs = ""

        query = f"""
            SELECT
                {", ".join(columns)}
            FROM repairs_measurement
            WHERE DATE(measured_at) >= '{start_date}'
                AND DATE(measured_at) <= '{end_date}'
                {filter_techs}
            GROUP BY tech
            ORDER BY tech
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params=params)
            columns = [column.name for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for row in results:
            if row["total_days"]:
                row["average_per_day"] = row["total_inch_feet"] / row["total_days"]
            else:
                row["average_per_day"] = None

        return results

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
