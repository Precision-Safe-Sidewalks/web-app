from abc import abstractmethod

from django.template import loader
from weasyprint import CSS, HTML

from repairs.models import InstructionSpecification
from repairs.models.constants import Hazard, SpecialCase, DRSpecification


class AbstractDocumentGenerator:
    """Abstract document generator"""

    @abstractmethod
    def generate(self, file_obj):
        """Generate the document"""
        raise NotImplementedError


class SurveyInstructionsGenerator:
    """Survey instructions PDF generator"""

    template_name = "documents/survey_instructions.html"
    stylesheet = "repairs/static/documents/survey_instructions.css"

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
        return {
            "instruction": self.instruction,
            "hazards": self.get_specification("H", Hazard.choices),
            "special_cases": self.get_specification("SC", SpecialCase.choices),
            "dr_specs": self.get_specification("DR", DRSpecification.choices),
        }

    def get_specification(self, spec_type, choices):
        """Return the specification data"""
        data = {}

        for key, label in choices:
            data[key] = {"label": label}
            data[key]["obj"] = self.instruction.specifications.filter(
                specification_type=spec_type, specification=key
            ).first()

        return data