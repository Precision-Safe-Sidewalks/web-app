from django.db import connection, models


class ProjectDashboard(models.Model):
    """Materialized view model for the dashboard table"""

    project_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    customer_id = models.IntegerField()
    customer_name = models.CharField(max_length=255)
    techs = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    last_date = models.DateTimeField(blank=True, null=True)
    hazards_expected = models.IntegerField()
    curb_length_expected = models.FloatField()
    inch_feet_expected = models.FloatField()
    square_feet_expected = models.FloatField()
    hazards_repaired = models.IntegerField()
    curb_length_repaired = models.FloatField()
    inch_feet_repaired = models.FloatField()
    square_feet_repaired = models.FloatField()
    bd_id = models.IntegerField(blank=True, null=True)
    bd_name = models.CharField(max_length=255)
    territory_id = models.IntegerField(blank=True, null=True)
    territory_label = models.CharField(max_length=10)

    class Meta:
        app_label = "repairs"
        db_table = "repairs_dashboard"
        managed = False

    @staticmethod
    def refresh():
        """Refresh the materialized view"""
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW repairs_dashboard")


class ProjectManagementDashboardView(models.Model):
    """PostgreSQL view for the project management dashboard"""

    sql = """
        WITH measurement_dates AS (
            SELECT
                project_id,
                MIN(measured_at) AS start_date,
                MAX(measured_at) AS last_date,
                SUM(curb_length) AS curb_length
            FROM repairs_measurement
                WHERE stage = 'PRODUCTION'
            GROUP BY project_id
        ), measurement_techs AS (
            SELECT
                project_id,
                STRING_AGG(initials, ', ') AS techs
            FROM (
                SELECT DISTINCT
                    project_id,
                    UPPER(CONCAT(SUBSTRING(tech, 1, 1), SUBSTRING(tech, 3, 1))) AS initials
                FROM repairs_measurement
                    WHERE stage = 'PRODUCTION'
                ORDER BY initials
            ) techs
            GROUP BY project_id
        ), measurement_expected AS (
            SELECT
                project_id,
                linear_feet_curb,
                COALESCE((hazards->'S'->'count')::int, 0) + COALESCE((hazards->'LS'->'count')::int, 0) + COALESCE((hazards->'MS'->'count')::int, 0) total,
                COALESCE((hazards->'S'->'inch_feet')::float, 0) + COALESCE((hazards->'LS'->'inch_feet')::float, 0) + COALESCE((hazards->'MS'->'inch_feet')::float, 0) inch_feet,
                COALESCE((hazards->'S'->'square_feet')::float, 0) + COALESCE((hazards->'LS'->'square_feet')::float, 0) + COALESCE((hazards->'MS'->'square_feet')::float, 0) square_feet
            FROM repairs_instruction
                WHERE stage = 'PRODUCTION'
        ), measurement_repaired AS (
            SELECT
                project_id,
                COUNT(*) AS total,
                SUM(inch_feet) AS inch_feet,
                SUM(area) AS area
            FROM repairs_measurement
            WHERE stage = 'PRODUCTION'
                AND special_case != 'C'
            GROUP BY project_id
        )
        SELECT
            p.id AS project_id,
            p.name,
            p.status,
            c.id AS customer_id,
            c.name AS customer_name,
            l.last_synced_at,
            mt.techs,
            md.start_date,
            md.last_date,
            me.total AS hazards_expected,
            me.linear_feet_curb AS curb_length_expected,
            me.inch_feet AS inch_feet_expected,
            me.square_feet AS square_feet_expected,
            COALESCE(mr.total, 0) AS hazards_repaired,
            COALESCE(md.curb_length, 0) AS curb_length_repaired,
            COALESCE(mr.inch_feet, 0) AS inch_feet_repaired,
            COALESCE(mr.area, 0) AS square_feet_repaired,
            u.id AS bd_id,
            u.full_name AS bd_name,
            t.id AS territory_id,
            t.label AS territory_label
        FROM repairs_project p
            JOIN customers_customer c ON p.customer_id = c.id
            JOIN core_territory t ON p.territory_id = t.id
            LEFT JOIN accounts_user u ON p.business_development_manager_id = u.id
            LEFT JOIN repairs_projectlayer l ON p.id = l.project_id AND l.stage = 'PRODUCTION'
            LEFT JOIN measurement_techs mt ON p.id = mt.project_id
            LEFT JOIN measurement_dates md ON p.id = md.project_id
            LEFT JOIN measurement_expected me ON p.id = me.project_id
            LEFT JOIN measurement_repaired mr ON p.id = mr.project_id
    """

    project_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    customer_id = models.IntegerField()
    customer_name = models.CharField(max_length=255)
    techs = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    last_date = models.DateTimeField(blank=True, null=True)
    hazards_expected = models.IntegerField()
    curb_length_expected = models.FloatField()
    inch_feet_expected = models.FloatField()
    square_feet_expected = models.FloatField()
    hazards_repaired = models.IntegerField()
    curb_length_repaired = models.FloatField()
    inch_feet_repaired = models.FloatField()
    square_feet_repaired = models.FloatField()
    bd_id = models.IntegerField(blank=True, null=True)
    bd_name = models.CharField(max_length=255)
    territory_id = models.IntegerField(blank=True, null=True)
    territory_label = models.CharField(max_length=10)

    class Meta:
        app_label = "repairs"
        db_table = "repairs_project_management_dashboard"
        managed = False
