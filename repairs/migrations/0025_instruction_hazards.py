# Generated by Django 4.2.4 on 2023-09-26 22:27

from django.db import migrations, models


def save_hazards(apps, schema_editor):
    Instruction = apps.get_model("repairs", "Instruction")

    for instruction in Instruction.objects.all():
        print(f"Saving instruction {instruction.pk}")
        instruction.save()


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0024_measurement_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="instruction",
            name="hazards",
            field=models.JSONField(default=dict, help_text="Aggregated hazard counts"),
        ),
        migrations.RunPython(save_hazards),
    ]