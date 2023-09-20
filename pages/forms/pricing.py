from django import forms

from repairs.models import PricingSheet


class PricingSheetInchFootForm(forms.ModelForm):
    """Inch foot pricing sheet form"""

    class Meta:
        model = PricingSheet
        fields = (
            "project",
            "estimated_sidewalk_miles",
            "surveyor_speed",
            "survey_hazards",
            "hazard_density",
            "panel_size",
            "distance_from_surveyor",
            "distance_from_ops",
            "commission_rate",
            "base_rate",
            "number_of_technicians",
        )
