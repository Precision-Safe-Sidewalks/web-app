from django.db import models


class ArcGISItem(models.Model):
    """ArcGIS Item"""

    class ItemType(models.TextChoices):
        WEB_MAP = "WEB_MAP"
        FEATURE_SERVICE = "FEATURE_SERVICE"

    item_id = models.CharField(max_length=50, db_index=True)
    item_type = models.CharField(max_length=25)
    title = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "third_party"
        db_table = "arcgis_item"
