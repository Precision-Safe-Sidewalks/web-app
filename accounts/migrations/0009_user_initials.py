# Generated by Django 4.2.4 on 2023-09-25 11:42

from django.db import migrations, models


def save_initials(apps, schema_editor):
    User = apps.get_model("accounts", "User")

    for user in User.objects.all():
        user.save()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_userphonenumber"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="initials",
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.RunPython(save_initials),
    ]
