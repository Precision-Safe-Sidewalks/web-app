# Generated by Django 4.2.4 on 2023-09-19 20:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0005_remove_contact_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
