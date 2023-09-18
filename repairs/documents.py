from abc import abstractmethod

from django.template import loader
from weasyprint import CSS, HTML

from repairs.models.constants import (
    DRSpecification,
    Hazard,
    ProductionCase,
    SpecialCase,
    Stage,
)


class AbstractDocumentGenerator:
    """Abstract document generator"""

    @abstractmethod
    def generate(self, file_obj):
        """Generate the document"""
        raise NotImplementedError


class BaseInstructionsGenerator:
    """Base Survey/Project instructions PDF generator"""

    template_name = None
    stylesheet = "repairs/static/documents/instructions.css"

    def __init__(self, instruction):
        self.instruction = instruction

    def generate(self, file_obj):
        """Generate the survey instructions PDF"""
        template = loader.get_template(self.template_name)
        context = self.get_context_data()
        content = template.render(context)
        css = CSS(self.stylesheet)
        html = HTML(string=content)
        html.write_pdf(file_obj, stylesheets=[css])

    def get_context_data(self):
        """Return the context data used to render the PDF"""
        return {}

    def get_specification(self, spec_type, choices):
        """Return the specification data"""
        data = {}

        for key, label in choices:
            data[key] = {"label": label}
            data[key]["obj"] = self.instruction.specifications.filter(
                specification_type=spec_type, specification=key
            ).first()

        return data


class SurveyInstructionsGenerator(BaseInstructionsGenerator):
    """Survey instructions PDF generator"""

    template_name = "documents/survey_instructions.html"

    def get_context_data(self):
        return {
            "instruction": self.instruction,
            "hazards": self.get_specification("H", Hazard.choices),
            "special_cases": self.get_specification("SC", SpecialCase.get_si_choices()),
            "dr_specs": self.get_specification("DR", DRSpecification.choices),
            "notes_placeholder": list(range(8)),
        }


class ProjectInstructionsGenerator(BaseInstructionsGenerator):
    """Project instructions PDF generator"""

    template_name = "documents/project_instructions.html"

    def get_context_data(self):
        return {
            "instruction": self.instruction,
            "hazards": self.get_hazard_counts(),
            "special_cases": self.get_specification("SC", SpecialCase.get_pi_choices()),
            "production_cases": self.get_specification("P", ProductionCase.choices),
            "dr_specs": self.get_specification("DR", DRSpecification.choices),
            "notes_placeholder": list(range(3)),
        }

    def get_hazard_counts(self):
        """Return the matrix of hazard counts"""
        hazards = {"labels": [], "counts": [], "sqft": [], "inft": []}
        measurements = self.instruction.project.measurements.filter(stage=Stage.SURVEY)

        for key, label in Hazard.choices:
            quick_description = Hazard.get_quick_description(key)
            queryset = measurements.filter(quick_description=quick_description)

            count = queryset.count()
            area_sqft = sum(
                [m.length * m.width for m in queryset if m.length and m.width]
            )
            area_inft = sum([m.inch_feet for m in queryset if m.inch_feet])

            hazards["labels"].append(Hazard.get_size(key))
            hazards["counts"].append(count)
            hazards["sqft"].append(area_sqft)
            hazards["inft"].append(area_inft)

        # Add in the totals
        hazards["labels"].append("TOTALS")
        hazards["counts"].append(sum(hazards["counts"]))
        hazards["sqft"].append(sum(hazards["sqft"]))
        hazards["inft"].append(sum(hazards["inft"]))

        return hazards
