import io
import json
import logging

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
from pages.forms.projects import (
    ProjectForm,
    ProjectMeasurementsForm,
)
from repairs.models import Measurement, Project, Instruction, InstructionSpecification
from repairs.models.constants import DRSpecification, Hazard, SpecialCase, Stage

LOGGER = logging.getLogger(__name__)


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
        filename = f"{slugify(project.name)}_measurements_{stage}.csv"

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
        context = super().get_context_data(**kwargs)
        context["instruction"] = project.instructions.get(stage=Stage.SURVEY)
        context["hazards"] = Hazard.choices
        context["special_cases"] = SpecialCase.choices
        context["dr_specifications"] = DRSpecification.choices
        context["pricing_models"] = InstructionSpecification.PricingModel.choices
        return context

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        instruction = project.instructions.get(project=project, stage=Stage.SURVEY)
        SpecificationType = InstructionSpecification.SpecificationType

        keep = []

        with transaction.atomic():
            for key in request.POST:
                spec_type = None
                spec = None
                defaults = {}

                if key.startswith("hazard-state"):
                    spec_type = SpecificationType.HAZARD
                    spec = key.split("-")[-1]
                    pricing_model = request.POST.get(f"hazard-pricing-model-{spec}")
                    defaults["pricing_model"] = pricing_model

                elif key.startswith("special-case-state"):
                    spec_type = SpecificationType.SPECIAL_CASE
                    spec = key.split("-")[-1]
                    note = request.POST.get(f"special-case-note-{spec}").strip()
                    defaults["note"] = note if note != "" else None

                elif key.startswith("dr-state"):
                    spec_type = SpecificationType.DR
                    spec = key.split("-")[-1]

                if spec_type and spec:
                    obj, _ = InstructionSpecification.objects.update_or_create(
                        instruction=instruction,
                        specification_type=spec_type,
                        specification=spec,
                        defaults=defaults,
                    )
                    keep.append(obj.id)

            InstructionSpecification.objects.exclude(
                instruction=instruction, id__in=keep
            ).delete()

        redirect_url = reverse("project-detail", kwargs={"pk": pk})
        return redirect(redirect_url)


class ProjectInstructionsView(TemplateView):
    template_name = "projects/project_instructions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["pk"])
        return context
