from django.db import models


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
