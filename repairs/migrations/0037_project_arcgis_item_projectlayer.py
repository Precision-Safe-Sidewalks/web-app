# Generated by Django 4.2.4 on 2024-01-13 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("third_party", "0001_initial"),
        ("repairs", "0036_alter_measurement_special_case"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="arcgis_item",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects",
                to="third_party.arcgisitem",
            ),
        ),
        migrations.CreateModel(
            name="ProjectLayer",
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
                (
                    "stage",
                    models.CharField(
                        choices=[("SURVEY", "Survey"), ("PRODUCTION", "Production")],
                        max_length=25,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "arcgis_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="third_party.arcgisitem",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="repairs.project",
                    ),
                ),
            ],
        ),
    ]
