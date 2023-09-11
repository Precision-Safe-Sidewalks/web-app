from django.db import models


class Stage(models.TextChoices):
    SURVEY = ("SURVEY", "Survey")
    PRODUCTION = ("PRODUCTION", "Production")


class SpecialCase(models.TextChoices):
    """Special case type choices"""

    APRONS = ("AP", "Aprons")
    ASPHALT = ("AS", "Asphalt")
    BOTTOM_HC = ("BHC", "Bottom HC")
    C2B = ("C2B", "C2B")
    CATCH_BASIN = ("CB", "Catch Basin")
    CURB = ("C", "Curb")
    DRIVEWAY = ("D", "Driveway")
    GUTTER_PAN = ("GP", "Gutter Pan")
    LEADWALK = ("L", "Leadwalk")
    METERS = ("ME", "Meters")
    MISSED = ("MI", "Missed")
    REPLACE = ("R", "Replace")
    SW2C = ("SW2C", "SW2C")


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
