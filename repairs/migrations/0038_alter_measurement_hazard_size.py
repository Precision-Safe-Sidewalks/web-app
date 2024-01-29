# Generated by Django 4.2.4 on 2024-01-29 19:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0037_project_arcgis_item_projectlayer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="measurement",
            name="hazard_size",
            field=models.CharField(
                blank=True,
                choices=[
                    ("S", "Small"),
                    ("M", "Medium"),
                    ("L", "Large"),
                    ("R", "Replace"),
                    ("O", "Other"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
