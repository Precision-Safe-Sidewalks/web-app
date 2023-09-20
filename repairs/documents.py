from abc import abstractmethod
from base64 import b64encode

from django.template import loader
from weasyprint import CSS, HTML

from repairs.models.constants import (
    DRSpecification,
    Hazard,
    ProjectSpecification,
    SpecialCase,
    Stage,
)


class AbstractDocumentGenerator:
    """Abstract document generator"""

    @abstractmethod
    def generate(self, file_obj):
        """Generate the document"""
        raise NotImplementedError


class BaseInstructionsGenerator(AbstractDocumentGenerator):
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
        context["hazards"] = self.get_hazards()
        context["project_specifications"] = self.get_specification(
            "P", ProjectSpecification.choices
        )
        context["special_cases"] = self.get_specification("SC", SpecialCase.choices)
        context["dr_specs"] = self.get_specification("DR", DRSpecification.choices)
        context["notes_placeholder"] = list(range(5))
        return context

    def get_hazards(self):
        """Return the matrix of hazards data"""
        hazards = {"labels": [], "counts": [], "sqft": [], "inft": []}
        queryset = self.instruction.project.measurements.filter(stage=Stage.SURVEY)

        for value, name in Hazard.choices:
            size = Hazard.get_size(value)
            data = queryset.filter(quick_description=size)

            label = name.split("Severe")[-1].strip()
            count = data.count()
            sqft = sum([m.length * m.width for m in data if m.length and m.width])
            inft = sum([m.inch_feet for m in data if m.inch_feet])

            hazards["labels"].append(label)
            hazards["counts"].append(count)
            hazards["sqft"].append(sqft)
            hazards["inft"].append(inft)

        # Compute the totals
        hazards["labels"].append("TOTALS")
        hazards["counts"].append(sum(hazards["counts"]))
        hazards["sqft"].append(sum(hazards["sqft"]))
        hazards["inft"].append(sum(hazards["inft"]))

        return hazards


class PricingSheetGenerator(AbstractDocumentGenerator):
    """Pricing sheet document generator"""

    def __init__(self, project):
        self.project = project

    def generate(self, file_obj):
        """Generate the Excel file"""
        pass

    def get_cell_data(self):
        """Return the dictionary of cell data to insert"""
        return {}


class PricingSheetInchFootGenerator(PricingSheetGenerator):
    """Pricing sheet (inch foot) document generator"""

    template_name = (
        "repairs/templates/documents/TEMP Pricing Inch Foot  - 8-29-2023- FINAL.xltx"
    )

    def get_cell_data(self):
        """Return the dictionary of cell data to insert"""
        return {}
