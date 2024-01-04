from django.db import models


class Segment(models.TextChoices):
    """Organization segment choices"""

    CAMPUS = ("CAMPUS", "Campus")
    HOA = ("HOA", "HOA")
    HA = ("HA", "HA")
    MUNI_LARGE = ("MUNI_LARGE", "Muni Large")
    MUNI_SMALL = ("MUNI_SMALL", "Muni Small")
    PROP_MGMT = "PROP_MGMT" "Prop Mgmt"
    RESIDENTIAL = ("RESIDENTIAL", "Residential")
    SCHOOLS_SYSTEMS = ("SCHOOLS_SYSTEMS", "Schools Systems")
    CONTRACTOR = ("CONTRACTOR", "Contractor")

    @classmethod
    def to_options(cls):
        """Return the list of options dictionaries"""
        return [{"key": k, "value": v} for (k, v) in cls.choices]
