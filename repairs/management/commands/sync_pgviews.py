from django.core.management.base import BaseCommand

from lib.pg_views import create_or_replace_views
from repairs.models import ProjectManagementDashboardView


class Command(BaseCommand):
    help = "Sync registered PostgreSQL views"

    def handle(self, *args, **options):
        models = (ProjectManagementDashboardView,)
        create_or_replace_views(models)
