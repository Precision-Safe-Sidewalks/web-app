import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from repairs.documents import SurveyInstructionsGenerator
from repairs.models import Instruction


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
