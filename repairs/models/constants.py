from django.db import models


class Stage(models.TextChoices):
    SURVEY = ("SURVEY", "Survey")
    PRODUCTION = ("PRODUCTION", "Production")


class SpecialCase(models.TextChoices):
    """Special case type choices"""

    REPLACE = ("R", "Replace")
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


class Hazard(models.TextChoices):
    """Hazard type choices"""

    LEAST_SEVERE = ("LS", 'Least Severe 1/4" to 1/2"')
    SEVERE = ("S", 'Severe 1/2" to 1"')
    MOST_SEVERE = ("MS", 'Most Severe 1" to 1 1/2"')

    @staticmethod
    def get_size(value):
        """Return the corresponding size"""
        if value == "LS":
            return "S"
        if value == "S":
            return "M"
        return "L"


class HazardTier(models.IntegerChoices):
    """Hazard tier type choices"""

    ABOVE_LS = (1, "All")
    ABOVE_S = (2, "Most Severe and Severe")
    ABOVE_MS = (3, "Most Severe")


class HazardDensity(models.IntegerChoices):
    """Hazard density type choices"""

    LOW = (1, "Low")
    AVG = (2, "Average")
    HIGH = (3, "High")


class DRSpecification(models.TextChoices):
    """Standard D&R specification type choices"""

    # TODO: improve how the CUSTOMX are handled

    NON_REPAIRABLE = ("NR", "Non-repairable")
    UNSTABLE = ("U", "Unstable, shifting sections, void")
    EXCESSIVE_CRACKING = ("EC", "Excessive cracking >2 cracks")
    CUSTOM1 = ("C1", "Custom 1")
    SIGNIFICANT_SPALLING = ("SS", "Significant spalling")
    LARGE_GAPS = ("LG", 'Large gaps >1"')
    SEVERE_CROSS_SLOPES = ("SCS", "Severe cross slopes >2.2%")
    CUSTOM2 = ("C2", "Custom 2")


class ProjectSpecification(models.IntegerChoices):
    """Project specification type choices"""

    DATA = (1, "Production Data")
    NTE = (2, "NTE or No Survey")
    ONLY_PINS = (3, "Only Pins")
    GD_STREETS = (4, "GD Streets Link")


class PricingModel(models.IntegerChoices):
    """Pricing model type choices"""

    INCH_FOOT = (1, "Inch Foot")
    SQUARE_FOOT = (2, "Square Foot")


class ReferenceImageMethod(models.IntegerChoices):
    """Reference image method type choices"""

    EVERYTHING = (1, "Pictures for everything")
    NUMBER_SIZES = (2, "Number/Sizes")


class Cut(models.IntegerChoices):
    """Cut type choices"""

    ONE_EIGHT = (1, "1:8")
    ONE_TEN = (2, "1:10")
    ONE_TWELVE = (3, "1:12")
    MULTIPLE = (4, "MS & S 1:12, LS 1:8")


class ContactMethod(models.IntegerChoices):
    """Contact method type choices"""

    CALL = (1, "Call")
    TEXT = (2, "Text")


class PanelSize(models.IntegerChoices):
    """Panel size type choices"""

    FIVE_FOOT = (1, "5 ft.")
    SIX_FOOT = (2, "6 ft.")
    SEVEN_FOOT = (3, "7 ft.")
