# Generated by Django 4.2.4 on 2023-12-02 13:19

from django.db import migrations, models
import repairs.models.pricing


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0034_alter_pricingsheet_estimated_sidewalk_miles"),
    ]

    operations = [
        migrations.AddField(
            model_name="pricingsheet",
            name="clins",
            field=models.JSONField(default=repairs.models.pricing.get_default_clins),
        ),
    ]