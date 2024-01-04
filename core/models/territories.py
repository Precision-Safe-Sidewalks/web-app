from django.db import models


class Territory(models.Model):
    """Categorical geographic region/territory"""

    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=10, unique=True)
    royalty_rate = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.label}"

    @classmethod
    def to_options(cls):
        """Return the list of options dictionaries"""
        queryset = cls.objects.order_by("name")
        return [{"key": t.id, "value": t.name} for t in queryset]
