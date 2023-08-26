# Generated by Django 4.2.4 on 2023-08-26 17:29

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import migrations


def set_default_site(apps, schema_editor):
    """Set the default site domain and name"""
    defaults = {"domain": "localhost:8000", "name": "localhost"}

    # FIXME: set the production domain/name
    if not settings.DEBUG:
        defaults["domain"] = ""
        defaults["name"] = ""

    Site.objects.update_or_create(pk=1, defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial"), ("sites", "0002_alter_domain_unique")]

    operations = [
        migrations.RunPython(set_default_site),
    ]
