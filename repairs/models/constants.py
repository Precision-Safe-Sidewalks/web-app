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
    METERS = ("MM", "Meters/Manholes")

    @classmethod
    def get_si_choices(cls):
        """Return the available choices for the SI"""
        return list(cls.choices)

    @classmethod
    def get_pi_choices(cls):
        """Return the available choices for the PI"""
        omit = {"R"}
        return list(filter(lambda c: c[0] not in omit, cls.choices))


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

    @classmethod
    def get_quick_description(cls, hazard):
        """Return the corresponding quick description"""
        index = {"LS": "S", "S": "M", "MS": "L"}

        if hazard in index:
            return QuickDescription(index[hazard])

        return None

    @classmethod
    def get_size(cls, hazard):
        """Return the corresponding size"""
        # TODO: implement a better way of handling this
        return cls(hazard).label.split("Severe")[-1].strip()


class DRSpecification(models.TextChoices):
    """Standard D&R specification type choices"""

    NON_REPAIRABLE = ("NR", "Non-repairable")
    UNSTABLE = ("U", "Unstable, shifting sections, void")
    EXCESSIVE_CRACKING = ("EC", "Excessive cracking >2 cracks")
    SIGNIFICANT_SPALLING = ("SS", "Significant spalling")
    LARGE_GAPS = ("LG", 'Large gaps >1"')
    SEVERE_CROSS_SLOPES = ("SCS", "Severe cross slopes >2.2%")


class ProductionCase(models.TextChoices):
    """Production case type choices"""

    PRODUCTION_DATA = ("PD", "Production data")
    NTE_OR_NO_SURVEY = ("NTE_NS", "NTE or no survey")
    ONLY_PINS = ("OP", "Only pins")
    GD_STREETS_LINK = ("GDSL", "GD streets link")
