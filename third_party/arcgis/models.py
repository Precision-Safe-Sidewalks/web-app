from django.db import models


class ArcGISItem(models.Model):
    """ArcGIS Item"""

    class ItemType(models.TextChoices):
        WEB_MAP = "WEB_MAP"
        FEATURE_SERVICE = "FEATURE_SERVICE"

    item_id = models.CharField(max_length=50, unique=True)
    item_type = models.CharField(max_length=25, choices=ItemType.choices)
    title = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    parent = models.ForeignKey(
        "ArcGISItem",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<ArcGISItem item_type={self.item_type} title={self.title}>"

    def __repr__(self):
        return str(self)

    class Meta:
        app_label = "third_party"
        db_table = "arcgis_item"
