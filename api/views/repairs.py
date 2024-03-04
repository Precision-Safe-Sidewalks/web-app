import io
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz

from django.contrib.gis.geos import Point
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters.projects import ProjectFilter
from api.serializers.projects import (
    PricingSheetCompleteSerializer,
    PricingSheetSerializer,
    ProjectLayerSerializer,
    ProjectSerializer,
    ProjectSummaryCompleteSerializer,
    ProjectSummarySerializer,
)
from repairs.documents import ProjectInstructionsGenerator, SurveyInstructionsGenerator
from repairs.models import (
    Instruction,
    Measurement,
    PricingSheetRequest,
    Project,
    ProjectDashboard,
    ProjectLayer,
    ProjectSummaryRequest,
)
from repairs.models.constants import PricingModel, QuickDescription, SpecialCase, Stage
from utils.aws import invoke_lambda_function
from utils.choices import value_of

LOGGER = logging.getLogger(__name__)


class SurveyInstructionsAPIView(APIView):
    """Generate the survey instructions document for download"""

    def get(self, request, pk):
        instruction = get_object_or_404(Instruction, pk=pk)
        preview = str(self.request.GET.get("preview")).lower() == "true"
        generator = SurveyInstructionsGenerator(instruction)

        if preview:
            content = generator.render()
            return HttpResponse(content)

        with io.BytesIO() as f:
            generator.generate(f)
            f.seek(0)

            filename = f"SI - {instruction.project.name}.pdf"
            resp = HttpResponse(f, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp


class ProjectInstructionsAPIView(APIView):
    """Generate the project instructions document for download"""

    def get(self, request, pk):
        instruction = get_object_or_404(Instruction, pk=pk)
        preview = str(self.request.GET.get("preview")).lower() == "true"
        generator = ProjectInstructionsGenerator(instruction)

        if preview:
            content = generator.render()
            return HttpResponse(content)

        with io.BytesIO() as f:
            generator.generate(f)
            f.seek(0)

            filename = f"PI - {instruction.project.name}.pdf"
            resp = HttpResponse(f, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp


class PricingSheetViewSet(viewsets.ViewSet):
    """Pricing sheet API view set"""

    def retrieve(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        request_id = request.GET.get("request_id")

        # If the request id is not supplied, this is a new request to
        # generate the pricing sheet. Trigger the lambda function and
        # return the request id for polling.
        if not request_id:
            req = PricingSheetRequest.objects.create(
                pricing_sheet=project.pricing_sheet
            )
            data = {"request_id": req.request_id}
            return Response(data, status=status.HTTP_202_ACCEPTED)

        # If the request id is supplied, check if the request has been
        # completed by the lambda function.
        req = get_object_or_404(project.pricing_sheet.requests, request_id=request_id)
        url = req.get_download_url()

        if not url:
            elapsed = timezone.now() - req.created_at
            data = {"elapsed": elapsed.seconds}

            # If the maximum timeout has been reached, indicate to the client
            # that the request has failed and polling should be terminated
            if elapsed.seconds >= 120:
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)

            return Response(data, status=status.HTTP_202_ACCEPTED)

        return Response({"url": url})

    @action(methods=["GET"], detail=True)
    def data(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = PricingSheetSerializer(project)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True)
    def complete(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = PricingSheetCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        request_id = data["request_id"]
        req = get_object_or_404(project.pricing_sheet.requests, request_id=request_id)

        req.s3_bucket = data["s3_bucket"]
        req.s3_key = data["s3_key"]
        req.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectSummaryViewSet(viewsets.ViewSet):
    """Project summary API viewset"""

    def retrieve(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        request_id = request.GET.get("request_id")

        # If the request id is not supplied, this is a new request to
        # generate the pricing sheet. Trigger the lambda function and
        # return the request id for polling.
        if not request_id:
            req = ProjectSummaryRequest.objects.create(project=project)
            data = {"request_id": req.request_id}
            return Response(data, status=status.HTTP_202_ACCEPTED)

        # If the request id is supplied, check if the request has been
        # completed by the lambda function.
        req = get_object_or_404(project.summary_requests, request_id=request_id)
        url = req.get_download_url()

        if not url:
            elapsed = timezone.now() - req.created_at
            data = {"elapsed": elapsed.seconds}

            # If the maximum timeout has been reached, indicate to the client
            # that the request has failed and polling should be terminated
            if elapsed.seconds >= 120:
                return Response(data, status=status.HTTP_408_REQUEST_TIMEOUT)

            return Response(data, status=status.HTTP_202_ACCEPTED)

        return Response({"url": url})

    @action(methods=["GET"], detail=True)
    def data(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSummarySerializer(project)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True)
    def complete(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSummaryCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        request_id = data["request_id"]
        req = get_object_or_404(project.summary_requests, request_id=request_id)

        req.s3_bucket = data["s3_bucket"]
        req.s3_key = data["s3_key"]
        req.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(viewsets.ModelViewSet):
    """Project API view set"""

    queryset = Project.objects.order_by("id")
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter

    @action(methods=["GET"], detail=True)
    def geocoding(self, request, pk=None):
        """Return the geocoding status"""
        project = self.get_object()
        stage = request.GET.get("stage", Stage.SURVEY)
        complete = project.measurements.filter(
            stage=stage, geocoded_address__isnull=False
        ).exists()
        return Response({"complete": complete})


class ProjectLayerViewSet(viewsets.ModelViewSet):
    """Project Layer API view set"""

    queryset = ProjectLayer.objects.order_by("id")
    serializer_class = ProjectLayerSerializer

    @action(methods=["POST"], detail=True)
    def sync(self, request, pk=None):
        """Synchronize the layer with ArcGIS"""
        layer = self.get_object()

        # If the layer is marked as IN_PROGRESS and was updated
        # less than 5 minutes ago, assume the sync is still running.
        if layer.status == ProjectLayer.Status.IN_PROGRESS:
            if timezone.now() > layer.updated_at + timedelta(minutes=5):
                return Response({"status": layer.status})
            else:
                LOGGER.info(
                    f"Previous sync for layer {layer.id} appears stuck. Re-syncing."
                )

        layer.status = ProjectLayer.Status.IN_PROGRESS
        layer.save()
        invoke_lambda_function("arcgis_sync", {"layer_id": layer.id})

        return Response({"status": layer.status})

    @action(methods=["POST"], detail=True)
    def features(self, request, pk=None):
        """Set the layer features from a GeoJSON FeatureCollection"""

        # Set the layer status to IN_PROGRESS to signal that the
        # synchronization has started
        layer = self.get_object()
        layer.status = ProjectLayer.Status.IN_PROGRESS
        layer.save()

        try:
            with transaction.atomic():
                invalid = set(
                    layer.project.measurements.filter(stage=layer.stage).values_list(
                        "id", flat=True
                    )
                )

                survey_group = None

                for feature in request.data.get("features", []):
                    geometry = feature["geometry"]
                    properties = feature["properties"]

                    timestamp = properties["CreationDate"] / 1000
                    measured_at = datetime.fromtimestamp(timestamp, tz=tz.utc)
                    survey_group = properties.get("StartStreetArea") or survey_group

                    defaults = {
                        "length": properties.get("Length"),
                        "width": properties.get("Width"),
                        "coordinate": Point(geometry["coordinates"], srid=4326),
                        "h1": properties.get("H1"),
                        "h2": properties.get("H2"),
                        "curb_length": properties.get("CurbLength"),
                        "measured_hazard_length": properties.get(
                            "MeasuredHazardLength"
                        ),
                        "inch_feet": properties.get("InchFeet"),
                        "special_case": value_of(
                            SpecialCase, properties.get("SpecialCase")
                        ),
                        "hazard_size": value_of(
                            QuickDescription,
                            properties.get("HazardSize"),
                        ),
                        "tech": properties["Creator"],
                        "note": properties.get("Notes"),
                        "survey_group": survey_group,
                        "slope": properties.get("Slope"),
                        "measured_at": measured_at,
                    }

                    for key in list(defaults):
                        if defaults[key] is None:
                            defaults.pop(key)

                    obj, _ = Measurement.objects.update_or_create(
                        project=layer.project,
                        stage=layer.stage,
                        object_id=properties["OBJECTID"],
                        defaults=defaults,
                    )

                    if obj.id in invalid:
                        invalid.remove(obj.id)

                # Delete any Measurements that where in the original set
                # for the project/stage but not in the latest sync
                Measurement.objects.filter(id__in=invalid).delete()

                # Update the last synced time and status
                layer.last_synced_at = timezone.now()
                layer.status = ProjectLayer.Status.COMPLETE
                layer.save()

                # For square foot pricing models, calculate the estimated sidewalk
                # miles from the measurements.
                if layer.project.pricing_model == PricingModel.SQUARE_FOOT:
                    layer.project.pricing_sheet.calculate_sidewalk_miles()

                # Trigger the Lambda function to reverse geocode the addresses
                # based on the coordinates by adding the (project_id, stage) to
                # the SQS queue
                payload = {"project_id": layer.project_id, "stage": layer.stage}
                invoke_lambda_function("geocoding", payload)

                # Refresh the dashboard view
                ProjectDashboard.refresh()

        # If the transaction failed, set the layer status to FAILED
        except Exception as exc:
            LOGGER.error(f"Error syncing layer: {exc}")
            layer.refresh_from_db()
            layer.status = ProjectLayer.Status.FAILED
            layer.save()

        return Response({"status": layer.status})
