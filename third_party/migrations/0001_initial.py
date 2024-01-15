# Generated by Django 4.2.4 on 2024-01-13 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ArcGISItem",
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
                ("item_id", models.CharField(max_length=50, unique=True)),
                (
                    "item_type",
                    models.CharField(
                        choices=[
                            ("WEB_MAP", "Web Map"),
                            ("FEATURE_SERVICE", "Feature Service"),
                        ],
                        max_length=25,
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("url", models.URLField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="third_party.arcgisitem",
                    ),
                ),
            ],
            options={
                "db_table": "arcgis_item",
            },
        ),
    ]
