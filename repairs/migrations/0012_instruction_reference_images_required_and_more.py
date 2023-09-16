# Generated by Django 4.2.4 on 2023-09-16 11:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0011_instruction_survey_method_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="instruction",
            name="reference_images_required",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instruction",
            name="reference_images_sizes",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]