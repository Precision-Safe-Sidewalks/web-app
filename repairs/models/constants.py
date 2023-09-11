from django.db import models


class Stage(models.TextChoices):
    SURVEY = ("SURVEY", "Survey")
    PRODUCTION = ("PRODUCTION", "Production")


class SpecialCase(models.TextChoices):
    """Special case type choices"""

    REPLACE = ("R", "Replace (D&R)")
    CURB = ("C", "Curb")
    BOTTOM_HC = ("BHC", "Bottom HC")
    GUTTER_PAN = ("GP", "Gutter Pan")
    CATCH_BASIN = ("CB", "Catch Basin")
    SW2C = ("SW2C", "SW2C")
    C2B = ("C2B", "C2B")
    ASPHALT = ("AS", "Asphalt")
    DRIVEWAY = ("D", "Driveway")
    APRONS = ("AP", "Aprons")
    LEADWALK = ("L", "Leadwalk")
    RECUTS = ("RC", "Recuts")
    METERES = ("MM", "Meters/Manholes")


class QuickDescription(models.TextChoices):
    """Quick description type choices"""

    SMALL = ("S", "Small")
    MEDIUM = ("M", "Medium")
    LARGE = ("L", "Large")


class DRSpecification(models.TextChoices):
    """Standard D&R specification type choices"""

    NON_REPAIRABLE = ("NR", "Non-repairable")
    UNSTABLE = ("U", "Unstable, shifting sections, void")
    EXCESSIVE_CRACKING = ("EC", "Excessive cracking >2 cracks")
    SIGNIFICANT_SPALLING = ("SS", "Significant spalling")
    LARGE_GAPS = ("LG", 'Large gaps >1"')
    SEVERE_CROSS_SLOPES = ("SCS", "Severe cross slopes >2.2%")
