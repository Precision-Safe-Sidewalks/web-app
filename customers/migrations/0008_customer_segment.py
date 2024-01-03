# Generated by Django 4.2.4 on 2024-01-03 20:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0007_contact_city_contact_state_contact_street_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="segment",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CAMPUS", "Campus"),
                    ("HOA", "HOA"),
                    ("HA", "HA"),
                    ("MUNI_LARGE", "Muni Large"),
                    ("MUNI_SMALL", "Muni Small"),
                    ("PROP_MGMTProp Mgmt", "Prop Mgmt"),
                    ("RESIDENTIAL", "Residential"),
                    ("SCHOOLS_SYSTEMS", "Schools Systems"),
                    ("CONTRACTOR", "Contractor"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]
