import io
import json
import logging
from datetime import datetime

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

from customers.models import Customer
from pages.forms.projects import ProjectForm, ProjectMeasurementsForm
from repairs.models import (
    InstructionContactNote,
    InstructionNote,
    InstructionSpecification,
    Measurement,
    Project,
)
from repairs.models.constants import DRSpecification, Hazard, SpecialCase, Stage

LOGGER = logging.getLogger(__name__)

User = get_user_model()


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"


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

        markers = project.get_measurements_geojson()
        context["measurements"] = json.dumps(markers, default=str)

        if project.measurements.exists():
            bbox = project.get_bbox(buffer_fraction=0.1)
            centroid = project.get_centroid().coords

            context["bbox"] = list(bbox)
            context["centroid"] = list(centroid)

        return context


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

        try:
            data = form.cleaned_data["file"].read().decode("utf-8-sig")
            with io.StringIO() as f:
                f.write(data)
                Measurement.import_from_csv(f, project=project, stage=stage)
        except ValidationError as exc:
            LOGGER.error(f"Error importing measurements: {exc}")
            redirect_url = f"{self.request.path}?error=Unable to parse the file"
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
        project.measurements.filter(stage=stage.upper()).delete()

        redirect_url = reverse("project-detail", kwargs={"pk": pk})
        return redirect(redirect_url)


class SurveyInstructionsView(TemplateView):
    template_name = "projects/survey_instructions.html"

    def get_context_data(self, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        instruction = project.instructions.get(stage=Stage.SURVEY)

        context = super().get_context_data(**kwargs)
        context["instruction"] = instruction
        context["notes"] = instruction.notes.order_by("created_at")
        context["hazards"] = Hazard.choices
        context["special_cases"] = SpecialCase.choices
        context["dr_specifications"] = DRSpecification.choices
        context["pricing_models"] = InstructionSpecification.PricingModel.choices
        context["surveyors"] = User.surveyors.all()
        context["error"] = self.request.GET.get("error")

        return context

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        instruction = project.instructions.get(project=project, stage=Stage.SURVEY)

        with transaction.atomic():
            self._errors = []

            self.process_surveyed_by(instruction)
            self.process_needed_by(instruction)
            self.process_survey_details(instruction)
            self.process_survey_method(instruction)
            self.process_contact_notes(instruction)
            self.process_specifications(instruction)
            self.process_reference_images(instruction)
            self.process_notes(instruction)

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
        needed_by = self.request.POST.get("needed_by")

        if not needed_by:
            instruction.needed_by = None
            instruction.needed_asap = False
            return
        else:
            needed_by = needed_by.strip().upper()

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

        survey_method_note = self.request.POST.get("survey_method_note", "").strip()
        instruction.survey_method_note = survey_method_note or None

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
            "special_case": InstructionSpecification.SpecificationType.SPECIAL_CASE,
            "dr": InstructionSpecification.SpecificationType.DR,
        }

        keep = []

        for form_key in self.request.POST:
            for spec_prefix, spec_type in index.items():
                prefix = f"{spec_prefix}:state:"

                if form_key.startswith(prefix):
                    spec = form_key.replace(prefix, "")
                    defaults = {}

                    for aux_key in ("pricing_model", "note"):
                        aux_prefix = f"{spec_prefix}:{aux_key}:{spec}"
                        defaults[aux_key] = self.request.POST.get(aux_prefix)

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
        reference_images_required = self.request.POST.get(
            "reference_images_required", 0
        )
        instruction.reference_images_required = int(reference_images_required)

        reference_images_sizes = self.request.POST.get("reference_images_sizes")
        instruction.reference_images_sizes = reference_images_sizes

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


class ProjectInstructionsView(TemplateView):
    template_name = "projects/project_instructions.html"

    def get_context_data(self, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        context = super().get_context_data(**kwargs)
        context["instruction"] = project.instructions.get(stage=Stage.SURVEY)
        context["hazards"] = Hazard.choices
        context["special_cases"] = SpecialCase.choices
        context["dr_specifications"] = DRSpecification.choices
        context["pricing_models"] = InstructionSpecification.PricingModel.choices
        context["surveyors"] = User.surveyors.all()
        context["error"] = self.request.GET.get("error")
        return context
