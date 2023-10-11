# Generated by Django 4.2.4 on 2023-10-09 12:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0027_projectsummaryrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="instruction",
            name="linear_feet_curb",
            field=models.FloatField(
                default=0, help_text="Approved PI curb linear feet"
            ),
        ),
    ]