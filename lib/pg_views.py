import logging

from django.db import connection, transaction

LOGGER = logging.getLogger(__name__)


def create_or_replace_views(models):
    """Create or replace the PostgreSQL views"""

    with transaction.atomic():
        with connection.cursor() as cursor:
            for model in models:
                LOGGER.info(f"Syncing PostgreSQL view: {model._meta.db_table}")
                sql = f"CREATE OR REPLACE VIEW {model._meta.db_table} AS {model.sql}"
                cursor.execute(sql)
