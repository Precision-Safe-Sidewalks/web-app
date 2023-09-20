from abc import abstractmethod
from base64 import b64encode

from django.template import loader
from weasyprint import CSS, HTML

from repairs.models.constants import DRSpecification, Hazard, SpecialCase


class AbstractDocumentGenerator:
    """Abstract document generator"""

    @abstractmethod
    def generate(self, file_obj):
        """Generate the document"""
        raise NotImplementedError


class BaseInstructionsGenerator:
    """Base instructions PDF generator"""

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
        """Return the context data to render"""
        return {
            "instruction": self.instruction,
            "logo": self.get_logo(),
        }

    def get_logo(self):
        """Return the base64 encoded logo"""
        with open("static/logos/pss_logo.png", "rb") as f:
            image = f.read()
            data = b64encode(image).decode("utf-8")
            return f"data:image/png;base64,{data}"

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
        context = super().get_context_data()
        context["hazards"] = self.get_specification("H", Hazard.choices)
        context["special_cases"] = self.get_specification("SC", SpecialCase.choices)
        context["dr_specs"] = self.get_specification("DR", DRSpecification.choices)
        context["notes_placeholder"] = list(range(5))
        return context


class ProjectInstructionsGenerator(BaseInstructionsGenerator):
    """Project instructions PDF generator"""

    template_name = "documents/project_instructions.html"

    def get_context_data(self):
        context = super().get_context_data()
        return context
