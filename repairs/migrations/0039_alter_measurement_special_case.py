# Generated by Django 4.2.4 on 2024-01-30 20:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0038_alter_measurement_hazard_size"),
    ]

    operations = [
        migrations.AlterField(
            model_name="measurement",
            name="special_case",
            field=models.CharField(
                blank=True,
                choices=[
                    ("C", "Curb"),
                    ("BHC", "Bottom HC"),
                    ("GP", "Gutter Pan"),
                    ("CB", "Catch Basin"),
                    ("SW2C", "SW2C"),
                    ("C2B", "C2B"),
                    ("AS", "Asphalt"),
                    ("D", "Driveway"),
                    ("AP", "Aprons"),
                    ("L", "Leadwalk"),
                    ("RC", "Recuts"),
                    ("MM", "Meters - Manholes"),
                    ("Q", "Quality"),
                    ("NONE", "None"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
