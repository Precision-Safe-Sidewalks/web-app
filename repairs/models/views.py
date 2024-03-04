from django.db import models


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
        raise NotImplementedError
