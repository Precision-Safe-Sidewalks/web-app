# Generated by Django 4.2.4 on 2024-01-15 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0039_alter_projectlayer_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectlayer",
            name="last_synced_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
