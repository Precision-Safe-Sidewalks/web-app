# Generated by Django 4.2.4 on 2023-09-16 11:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0009_instructioncontactnote"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="details",
        ),
        migrations.AddField(
            model_name="instruction",
            name="details",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="po_number",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
