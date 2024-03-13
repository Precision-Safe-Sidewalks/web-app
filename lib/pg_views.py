from django.db import connection, transaction


def create_or_replace_views(models):
    """Create or replace the PostgreSQL views"""

    with transaction.atomic():
        with connection.cursor() as cursor:
            for model in models:
                sql = f"CREATE OR REPLACE VIEW {model._meta.db_table} AS {model.sql}"
                cursor.execute(sql)
