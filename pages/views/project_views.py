import io
import json
import logging
from datetime import datetime

import chardet
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.text import slugify
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from pydantic import ValidationError

from core.models import Territory
from customers.constants import Segment
from customers.models import Customer
from pages.forms.projects import (
    PricingSheetContactForm,
    PricingSheetInchFootForm,
    PricingSheetSquareFootForm,
    ProjectForm,
    ProjectMeasurementsForm,
)
from repairs.models import (
    InstructionContactNote,
    InstructionNote,
    InstructionSpecification,
    Measurement,
    Project,
    ProjectLayer,
)
from repairs.models.constants import (
    ContactMethod,
    Cut,
    DRSpecification,
    Hazard,
    PricingModel,
    ProjectSpecification,
    QuickDescription,
    ReferenceImageMethod,
    SpecialCase,
    Stage,
)
from third_party.models import ArcGISItem
from utils.aws import invoke_lambda_function

LOGGER = logging.getLogger(__name__)

User = get_user_model()


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_filters"] = self.get_table_filters()
        return context

    def get_table_filters(self):
        """Return the dictionary of table filters"""
        return json.dumps(
            [
                {
                    "label": "BD",
                    "field": "business_development_manager",
                    "options": User.bdm.to_options(),
                },
                {
                    "label": "Territory",
                    "field": "territory",
                    "options": Territory.to_options(),
                },
                {
                    "label": "Stage",
                    "field": "status",
                    "options": Project.Status.to_options(),
                },
                {
                    "label": "Segment",
                    "field": "segment",
                    "options": Segment.to_options(),
                },
            ]
        )


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        project = self.get_object()
        context = super().get_context_data(**kwargs)

        context["si"] = project.instructions.filter(stage=Stage.SURVEY).first()
        context["pi"] = project.instructions.filter(stage=Stage.PRODUCTION).first()
        context["statuses"] = Project.Status.choices
        context["map_legend"] = self.get_map_legend()

        if project.measurements.exists():
            centroid = project.get_centroid().coords
            context["centroid"] = list(centroid)

        return context

    def get_map_legend(self):
        """Return the map legend"""
        queryset = self.get_object().measurements.all()
        legend = {"stages": [], "hazard_sizes": [], "special_cases": []}

        for stage, label in Stage.choices:
            if queryset.filter(stage=stage).exists():
                legend["stages"].append(label)

        for hazard_size, label in QuickDescription.choices:
            if queryset.filter(hazard_size=hazard_size).exists():
                legend["hazard_sizes"].append(label)

        for special_case, label in SpecialCase.choices:
            if queryset.filter(special_case=special_case).exists():
                legend["special_cases"].append(label)

        return legend


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["customer"] = self.kwargs["pk"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = get_object_or_404(Customer, pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return reverse("customer-detail", kwargs={"pk": self.kwargs["pk"]})


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def get_initial(self):
        project = self.get_object()
        initial = super().get_initial()
        initial["primary_contact"] = project.primary_contact
        initial["secondary_contact"] = project.secondary_contact
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.get_object().customer
        return context

    def get_success_url(self):
        return reverse("project-detail", kwargs={"pk": self.kwargs["pk"]})


class ProjectStatusUpdateView(View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.status = int(request.POST.get("status"))
        project.save()

        redirect_url = reverse("project-detail", kwargs={"pk": self.kwargs["pk"]})
        return redirect(redirect_url)


class ProjectWebMapView(DetailView):
    model = Project
    template_name = "projects/project_web_map.html"
    context_object_name = "project"

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        layers = []

        with transaction.atomic():
            web_map = int(request.POST.get("web_map"))
            item = ArcGISItem.objects.filter(pk=web_map).first()

            if web_map != project.arcgis_item != item and item is not None:
                project.arcgis_item_id = item
                project.save()

                project.layers.all().delete()
                project.measurements.all().delete()

                for child in item.children.all():
                    if child.title.startswith("PSS Survey"):
                        layer = ProjectLayer.objects.create(
                            project=project, stage=Stage.SURVEY, arcgis_item=child
                        )
                        layers.append(layer.id)

                    elif child.title.startswith("PSS Repair"):
                        layer = ProjectLayer.objects.create(
                            project=project, stage=Stage.PRODUCTION, arcgis_item=child
                        )
                        layers.append(layer.id)

        for layer in layers:
            invoke_lambda_function("arcgis_sync", {"layer_id": layer})

        redirect_url = reverse("project-detail", kwargs={"pk": self.kwargs["pk"]})
        return redirect(redirect_url)


class ProjectMeasurementsImportView(FormView):
    form_class = ProjectMeasurementsForm
    template_name = "projects/project_measurements_form.html"

    def get_context_data(self, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        stage = self.kwargs["stage"].lower()

        context = super().get_context_data(**kwargs)
        context["project"] = project
        context["stage"] = stage
        context["error"] = self.request.GET.get("error")

        if stage == "survey":
            context["is_replace"] = project.has_survey_measurements
        else:
            context["is_replace"] = project.has_production_measurements

        return context

    def get_success_url(self):
        return reverse("project-detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        stage = self.kwargs["stage"].strip().upper()

        raw_data = form.cleaned_data["file"].read()
        encoding = chardet.detect(raw_data)["encoding"]
        data = raw_data.decode(encoding)

        try:
            with io.StringIO() as file_obj:
                file_obj.write(data)
                Measurement.import_from_csv(file_obj, project=project, stage=stage)
        except ValidationError as exc:
            error = exc.errors()[0]
            reason = error.get("msg", "Unable to parse the file")
            columns = ", ".join(error.get("loc", []))
            message = f"[{columns}]: {reason}"

            LOGGER.error(f"Error importing measurements: {exc}")
            redirect_url = f"{self.request.path}?error={message}"

            return redirect(redirect_url)

        return super().form_valid(form)


class ProjectMeasurementsExportView(View):
    """Download the project measurements CSV"""

    def get(self, request, pk, stage):
        project = get_object_or_404(Project, pk=pk)
        filename = f"{slugify(project.name)}_data_{stage}.csv"

        with io.StringIO() as f:
            Measurement.export_to_csv(f, project, stage.upper())

            resp = HttpResponse(f, content_type="text/csv")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp


class ProjectMeasurementsClearView(View):
    def post(self, request, pk, stage):
        project = get_object_or_404(Project, pk=pk)
        stage = stage.upper()

        with transaction.atomic():
            project.measurements.filter(stage=stage).delete()

            # If the layer with a matching stage exists, update
            # the sync status to reflect the deleted data.
            if layer := project.layers.filter(stage=stage).first():
                layer.status = ProjectLayer.Status.NOT_SYNCED
                layer.save()

        redirect_url = reverse("project-detail", kwargs={"pk": pk})
        return redirect(redirect_url)


class BaseInstructionsView(TemplateView):
    stage = None

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        instruction = project.instructions.get(project=project, stage=self.stage)

        with transaction.atomic():
            self._errors = []

            self.process_surveyed_by(instruction)
            self.process_needed_by(instruction)
            self.process_survey_details(instruction)
            self.process_survey_method(instruction)
            self.process_supplements(instruction)
            self.process_cut(instruction)
            self.process_linear_feet_curb(instruction)
            self.process_hazards(instruction)
            self.process_contact_method(instruction)
            self.process_contact_notes(instruction)
            self.process_specifications(instruction)
            self.process_reference_images(instruction)
            self.process_notes(instruction)
            self.process_debris_notes(instruction)
            self.process_checklist(instruction)
            self.process_published(instruction)

            instruction.save()

        if self._errors:
            error = "; ".join(self._errors)
            redirect_url = request.path + f"?error={error}"
            return redirect(redirect_url)

        redirect_url = reverse("project-detail", kwargs={"pk": pk})
        return redirect(redirect_url)

    def process_surveyed_by(self, instruction):
        """Process the surveyed_by form field"""
        surveyed_by = self.request.POST.get("surveyed_by")

        if surveyed_by:
            instruction.surveyed_by = User.objects.filter(pk=surveyed_by).first()
        else:
            instruction.surveyed_by = None

    def process_needed_by(self, instruction):
        """Process the needed_by/needed_asap fields"""
        needed_by = self.request.POST.get("needed_by") or "TBD"
        needed_by = needed_by.upper().strip()

        if needed_by == "TBD":
            instruction.needed_by = None
            instruction.needed_asap = False
            return

        if needed_by == "ASAP":
            instruction.needed_by = None
            instruction.needed_asap = True
            return

        try:
            needed_by = datetime.strptime(needed_by, "%m/%d/%Y")
            instruction.needed_by = needed_by.date()
            instruction.needed_asap = False
        except ValueError:
            self._errors.append("Invalid needed by date")

    def process_survey_details(self, instruction):
        """Process the survey details"""
        details = self.request.POST.get("details", "").strip()
        instruction.details = details or None

    def process_survey_method(self, instruction):
        """Process the survey method"""
        survey_method = self.request.POST.get("survey_method", "").strip()
        instruction.survey_method = survey_method or None

    def process_supplements(self, instruction):
        """Process the supplemental PDFs"""
        instruction.include_fieldmaps_supplement = False
        instruction.include_bidboss_supplement = False

        if self.request.POST.get("include_fieldmaps_supplement") == "on":
            instruction.include_fieldmaps_supplement = True

        if self.request.POST.get("include_bidboss_supplement") == "on":
            instruction.include_bidboss_supplement = True

    def process_cut(self, instruction):
        """Process the cut"""
        cut = int(self.request.POST.get("cut", 1))
        instruction.cut = cut

    def process_linear_feet_curb(self, instruction):
        """Process the linear feet curb"""
        linear_feet_curb = float(self.request.POST.get("linear_feet_curb", 0))
        instruction.linear_feet_curb = linear_feet_curb

    def process_hazards(self, instruction):
        """ "Process the instruction hazards aggregation"""
        if instruction.stage != Stage.PRODUCTION:
            return

        dtypes = {"count": int, "square_feet": float, "inch_feet": float}

        for key, value in self.request.POST.items():
            if key.startswith("hazards:"):
                _, metric, hazard = key.split(":")
                dtype = dtypes[metric]
                value = value or 0
                instruction.hazards[hazard][metric] = dtype(value)

    def process_contact_method(self, instruction):
        """Process the instruction contact method"""
        contact_method = int(self.request.POST.get("contact_method", 1))
        instruction.contact_method = contact_method

    def process_contact_notes(self, instruction):
        """Process the instruction contact notes"""
        keep = []

        for key in ("primary", "secondary"):
            note = self.request.POST.get(f"contact_note:{key}", "").strip()
            contact = getattr(instruction.project, f"{key}_contact", None)

            if note and contact:
                obj, _ = InstructionContactNote.objects.update_or_create(
                    instruction=instruction, contact=contact, note=note
                )
                keep.append(obj.pk)

        instruction.contact_notes.exclude(pk__in=keep).delete()

    def process_specifications(self, instruction):
        """Process the instruction special cases"""
        index = {
            "hazard": InstructionSpecification.SpecificationType.HAZARD,
            "hazard_size": InstructionSpecification.SpecificationType.HAZARD_SIZE,
            "special_case": InstructionSpecification.SpecificationType.SPECIAL_CASE,
            "dr": InstructionSpecification.SpecificationType.DR,
            "project": InstructionSpecification.SpecificationType.PROJECT,
        }

        keep = []

        for form_key in self.request.POST:
            for spec_prefix, spec_type in index.items():
                prefix = f"{spec_prefix}:state:"

                if form_key.startswith(prefix):
                    spec = form_key.replace(prefix, "")
                    defaults = {}

                    for aux_key in ("note",):
                        aux_prefix = f"{spec_prefix}:{aux_key}:{spec}"
                        defaults[aux_key] = self.request.POST.get(aux_prefix)

                    # TODO: improve how this is stored
                    if spec_prefix == "dr" and spec in ("C1", "C2"):
                        defaults["note"] = self.request.POST.get(f"dr:state:{spec}")

                    obj, _ = InstructionSpecification.objects.update_or_create(
                        instruction=instruction,
                        specification_type=spec_type,
                        specification=spec,
                        defaults=defaults,
                    )

                    keep.append(obj.pk)

        instruction.specifications.exclude(pk__in=keep).delete()

    def process_reference_images(self, instruction):
        """Process the reference images"""
        method = int(self.request.POST.get("reference_images_method", 1))

        if method == ReferenceImageMethod.EVERYTHING.value:
            instruction.reference_images_method = method
            return

        if method == ReferenceImageMethod.NUMBER_SIZES:
            number_required = self.request.POST.get("reference_images_required", 0)
            sizes = self.request.POST.get("reference_images_sizes")
            curbs = self.request.POST.get("reference_images_curbs") == "on"

            instruction.reference_images_method = method
            instruction.reference_images_required = int(number_required)
            instruction.reference_images_sizes = sizes
            instruction.reference_images_curbs = curbs

    def process_notes(self, instruction):
        """Process the instruction notes"""
        keep = []

        for form_key in self.request.POST:
            if form_key.startswith("note:new:"):
                if note := self.request.POST.get(form_key).strip():
                    obj = InstructionNote.objects.create(
                        instruction=instruction, note=note
                    )
                    keep.append(obj.pk)

            elif form_key.startswith("note:"):
                if note := self.request.POST.get(form_key).strip():
                    pk = int(form_key.replace("note:", ""))
                    InstructionNote.objects.filter(
                        instruction=instruction, pk=pk
                    ).update(note=note)
                    keep.append(pk)

        instruction.notes.exclude(pk__in=keep).delete()

    def process_debris_notes(self, instruction):
        """Process the debris and trailer parking notes"""
        instruction.debris_notes = self.request.POST.get("debris_notes")

    def process_checklist(self, instruction):
        """Process the instruction checklist"""

        for form_key in self.request.POST:
            if form_key.startswith("checklist:"):
                pk = int(form_key.replace("checklist:", ""))
                obj = instruction.checklist.get(pk=pk)
                obj.response = self.request.POST.get(form_key, "").strip()
                obj.save()

    def process_published(self, instruction):
        """Process the instruction published status"""
        published = self.request.POST.get("published") == "on"
        instruction.published = published


class SurveyInstructionsView(BaseInstructionsView):
    template_name = "projects/survey_instructions.html"
    stage = Stage.SURVEY

    def get_context_data(self, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        instruction = project.instructions.get(stage=self.stage)

        context = super().get_context_data(**kwargs)
        context["instruction"] = instruction
        context["notes"] = instruction.notes.order_by("created_at")
        context["hazards"] = Hazard.choices
        context["special_cases"] = SpecialCase.choices
        context["dr_specifications"] = DRSpecification.choices
        context["surveyors"] = User.surveyors.all()
        context["reference_image_methods"] = ReferenceImageMethod.choices
        context["error"] = self.request.GET.get("error")

        return context


class ProjectInstructionsView(BaseInstructionsView):
    template_name = "projects/project_instructions.html"
    stage = Stage.PRODUCTION

    def get_context_data(self, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        instruction = project.instructions.get(stage=self.stage)

        # TODO: find a better location to update the hazard defaults
        if not instruction.hazards:
            instruction.hazards = instruction.get_default_hazards()
            instruction.save()

        context = super().get_context_data(**kwargs)
        context["instruction"] = instruction
        context["notes"] = instruction.notes.order_by("created_at")
        context["cuts"] = Cut.choices
        context["project_specifications"] = ProjectSpecification.choices
        context["special_cases"] = SpecialCase.choices
        context["dr_specifications"] = DRSpecification.choices
        context["contact_methods"] = ContactMethod.choices
        context["checklist"] = instruction.get_checklist()
        context["surveyors"] = User.surveyors.all()
        context["reference_image_methods"] = ReferenceImageMethod.choices
        context["error"] = self.request.GET.get("error")

        return context


class PricingSheetView(TemplateView):
    def get_object(self):
        """Return the Project object"""
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def get_template_names(self):
        """Return the template based on the pricing model"""
        project = self.get_object()

        if project.pricing_model == PricingModel.SQUARE_FOOT:
            return "projects/pricing_sheet_square_foot.html"

        return "projects/pricing_sheet_inch_foot.html"

    def get_form_class(self):
        """Return the form class"""
        project = self.get_object()

        if project.pricing_model == PricingModel.SQUARE_FOOT:
            return PricingSheetSquareFootForm

        return PricingSheetInchFootForm

    def get_context_data(self, **kwargs):
        project = self.get_object()
        pricing_sheet = project.pricing_sheet
        contact = pricing_sheet.get_contact()

        context = super().get_context_data(**kwargs)
        context["project"] = project
        context["form"] = self.get_form_class()(instance=pricing_sheet)
        context["contact_form"] = PricingSheetContactForm(instance=contact)
        context["contact_type"] = contact.contact_type if contact else None
        context["contact_exists"] = contact is not None
        context["clins"] = pricing_sheet.clins

        return context

    def post(self, request, pk):
        project = self.get_object()
        pricing_sheet = project.pricing_sheet
        contact = pricing_sheet.get_contact()

        # TODO: find a better way to do this
        request.POST._mutable = True
        request.POST["contact:pricing_sheet"] = pricing_sheet.pk
        request.POST._mutable = False

        form = self.get_form_class()(request.POST, instance=project.pricing_sheet)
        contact_form = PricingSheetContactForm(request.POST, instance=contact)

        is_valid = form.is_valid()

        if project.pricing_model == PricingModel.INCH_FOOT:
            is_valid = is_valid and contact_form.is_valid()

        if is_valid:
            with transaction.atomic():
                form.save()

                if project.pricing_model == PricingModel.INCH_FOOT:
                    contact_form.cleaned_data["pricing_sheet"] = pricing_sheet
                    contact_form.save()

            redirect_url = reverse("project-detail", kwargs={"pk": self.kwargs["pk"]})
            return redirect(redirect_url)

        # TODO: improve the errors for context
        redirect_url = request.path + "?errors=Unable to save the pricing sheet"
        return redirect(redirect_url)
