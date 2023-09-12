# Generated by Django 4.2.4 on 2023-09-12 12:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0002_instruction_instructionnote_instructionspecification"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="instructionspecification",
            name="area",
        ),
        migrations.AddField(
            model_name="instructionspecification",
            name="pricing_model",
            field=models.CharField(
                blank=True,
                choices=[("S", "Standard"), ("SQFT", "Square foot")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="measurement",
            name="special_case",
            field=models.CharField(
                blank=True,
                choices=[
                    ("R", "Replace (D&R)"),
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
                    ("MM", "Meters/Manholes"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
