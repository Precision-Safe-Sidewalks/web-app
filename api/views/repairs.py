import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.projects import PricingSheetSerializer
from repairs.documents import ProjectInstructionsGenerator, SurveyInstructionsGenerator
from repairs.models import (
    Instruction,
    PricingSheetRequest,
    Project,
    ProjectSummaryRequest,
)


class SurveyInstructionsAPIView(APIView):
    """Generate the survey instructions document for download"""

    def get(self, request, pk):
        instruction = get_object_or_404(Instruction, pk=pk)
        generator = SurveyInstructionsGenerator(instruction)

        with io.BytesIO() as f:
            generator.generate(f)
            f.seek(0)

            filename = f"{instruction.project.name} - SI.pdf"
            resp = HttpResponse(f, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp


class ProjectInstructionsAPIView(APIView):
    """Generate the project instructions document for download"""

    def get(self, request, pk):
        instruction = get_object_or_404(Instruction, pk=pk)
        generator = ProjectInstructionsGenerator(instruction)

        with io.BytesIO() as f:
            generator.generate(f)
            f.seek(0)

            filename = f"{instruction.project.name} - PI.pdf"
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
        raise NotImplementedError


class ProjectSummaryAPIView(APIView):
    """Generate the project summary document for download"""

    def get(self, request, pk):
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
