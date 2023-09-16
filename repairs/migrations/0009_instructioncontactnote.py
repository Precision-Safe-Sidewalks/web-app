# Generated by Django 4.2.4 on 2023-09-15 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0005_remove_contact_notes"),
        ("repairs", "0008_alter_project_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="InstructionContactNote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("note", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customers.contact",
                    ),
                ),
                (
                    "instruction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contact_notes",
                        to="repairs.instruction",
                    ),
                ),
            ],
        ),
    ]