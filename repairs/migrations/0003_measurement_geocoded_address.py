# Generated by Django 4.2.4 on 2023-08-31 21:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0002_measurement_measurementimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="measurement",
            name="geocoded_address",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
