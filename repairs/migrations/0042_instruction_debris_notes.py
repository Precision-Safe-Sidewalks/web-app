# Generated by Django 4.2.4 on 2024-02-20 14:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0041_instruction_include_bidboss_supplement_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="instruction",
            name="debris_notes",
            field=models.TextField(blank=True, null=True),
        ),
    ]
