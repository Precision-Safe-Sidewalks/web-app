from abc import abstractmethod

from django.template import loader
from weasyprint import CSS, HTML

from repairs.models.constants import SpecialCase


class AbstractDocumentGenerator:
    """Abstract document generator"""

    @abstractmethod
    def generate(self, file_obj):
        """Generate the document"""
        raise NotImplementedError


class SurveyInstructionsGenerator:
    """Survey instructions PDF generator"""

    def __init__(self, project):
        self.project = project

    def generate(self, file_obj):
        """Generate the survey instructions PDF"""

        template = loader.get_template("documents/survey_instructions.html")
        context = {
            "project": self.project,
            "special_cases": SpecialCase.choices,
        }
        content = template.render(context)

        css = CSS("repairs/static/documents/survey_instructions.css")
        html = HTML(string=content)
        html.write_pdf(file_obj, stylesheets=[css])
