import io
from abc import abstractmethod
from base64 import b64encode

from django.contrib.staticfiles import finders
from django.template import loader
from pypdf import PdfWriter
from weasyprint import CSS, HTML

from repairs.models.constants import (
    DRSpecification,
    Hazard,
    ProjectSpecification,
    QuickDescription,
    SpecialCase,
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
        with io.BytesIO() as document:
            content = self.render()
            css = CSS(self.stylesheet)
            html = HTML(string=content)
            html.write_pdf(document, stylesheets=[css])

            document.seek(0)
            merger = PdfWriter()
            merger.append(fileobj=document)

            for supplement in self.get_supplemental_files():
                merger.append(supplement)

            merger.write(file_obj)
            merger.close()

    def render(self):
        """Render the template to HTML"""
        template = loader.get_template(self.template_name)
        context = self.get_context_data()
        content = template.render(context)
        return content

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

    def get_supplemental_files(self):
        """Return the list of supplemental files"""
        return []


class SurveyInstructionsGenerator(BaseInstructionsGenerator):
    """Survey instructions PDF generator"""

    template_name = "documents/survey_instructions.html"
    instructions_fieldmaps = "assets/FieldMaps Survey Instructions for SI.pdf"

    def get_context_data(self):
        context = super().get_context_data()
        context["hazards"] = self.get_specification("H", Hazard.choices)
        context["hazard_sizes"] = self.get_specification("HS", QuickDescription.choices)
        context["special_cases"] = self.get_specification("SC", SpecialCase.choices)
        context["dr_specs"] = self.get_specification("DR", DRSpecification.choices)
        context["notes_placeholder"] = list(range(3))
        return context

    def get_supplemental_files(self):
        """Return the supplemental files"""
        supplements = []

        if self.instruction.include_fieldmaps_supplement:
            supplements.append(finders.find(self.instructions_fieldmaps))

        return supplements


class ProjectInstructionsGenerator(BaseInstructionsGenerator):
    """Project instructions PDF generator"""

    template_name = "documents/project_instructions.html"
    instruction_fieldmaps = "assets/FieldMaps Repair Layer Instructions for PIs.pdf"
    instruction_bidboss = "assets/BidBoss Instructions - 2-15-24.pdf"

    def get_context_data(self):
        context = super().get_context_data()
        context["hazards"] = self.get_hazards()
        context["hazard_sizes"] = self.get_specification("HS", QuickDescription.choices)
        context["project_specifications"] = self.get_specification(
            "P", ProjectSpecification.choices
        )
        context["special_cases"] = self.get_specification("SC", SpecialCase.choices)
        context["dr_specs"] = self.get_specification("DR", DRSpecification.choices)
        context["notes_placeholder"] = list(range(3))
        context[
            "linear_feet_curb_note"
        ] = f"{self.instruction.linear_feet_curb:g} linear feet."
        return context

    def get_hazards(self):
        """Return the matrix of hazards data"""
        hazards = {"labels": [], "counts": [], "sqft": [], "inft": []}

        for value, name in Hazard.choices:
            data = self.instruction.hazards.get(value, {})

            label = name.split("Severe")[-1].strip()
            count = data.get("count", 0)
            sqft = data.get("square_feet", 0)
            inft = data.get("inch_feet", 0)

            hazards["labels"].append(label)
            hazards["counts"].append(count)
            hazards["sqft"].append(sqft)
            hazards["inft"].append(inft)

        # Compute the totals
        hazards["labels"].append("TOTALS")
        hazards["counts"].append(sum(hazards["counts"]))
        hazards["sqft"].append(sum(hazards["sqft"]))
        hazards["inft"].append(sum(hazards["inft"]))

        # Coerce any floats to integers if applicable
        for key in hazards:
            for i, value in enumerate(hazards[key]):
                if isinstance(value, float) and value.is_integer():
                    hazards[key][i] = int(value)

        return hazards

    def get_supplemental_files(self):
        """Return the supplemental files"""
        supplements = []

        if self.instruction.include_fieldmaps_supplement:
            supplements.append(finders.find(self.instructions_fieldmaps))

        if self.instruction.include_bidboss_supplement:
            supplements.append(finders.find(self.instructions_bidboss))

        return supplements
