# Generated by Django 4.2.4 on 2023-09-26 23:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0025_instruction_hazards"),
    ]

    operations = [
        migrations.RenameField(
            model_name="measurement",
            old_name="group",
            new_name="survey_group",
        ),
    ]