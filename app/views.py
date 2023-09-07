from django.http import JsonResponse


def status(request):
    """Application status/healtcheck view"""
    return JsonResponse({"status": "healthy"})
