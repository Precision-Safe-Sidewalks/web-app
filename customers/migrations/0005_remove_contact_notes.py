# Generated by Django 4.2.4 on 2023-09-15 10:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0004_contact_notes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contact",
            name="notes",
        ),
    ]
