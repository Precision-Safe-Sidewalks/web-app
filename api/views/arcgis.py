import logging
import re

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers.arcgis import ArcGISItemSerializer
from repairs.models import Project
from third_party.arcgis.models import ArcGISItem

logger = logging.getLogger(__name__)


RE_ITEM_TITLE = re.compile(r"^PSS\s+(?P<name>.*)\s+(?P<template_date>\d{6})$")


class ArcGISItemViewSet(ModelViewSet):
    """ArcGIS Item API view set"""

    queryset = ArcGISItem.objects.order_by("id")
    serializer_class = ArcGISItemSerializer
    # filterset_class = ArcGISItemFilter

    @action(methods=["GET", "POST"], detail=False)
    def match(self, request):
        """Match the ArcGIS web maps to a Project"""
        items = ArcGISItem.objects.filter(
            item_type=ArcGISItem.ItemType.WEB_MAP,
            title__startswith="PSS",
            projects__isnull=True,
        )

        matches = 0

        for item in items:
            if match := RE_ITEM_TITLE.match(item.title):
                name = match.group("name")
                projects = Project.objects.filter(name=name, arcgis_item__isnull=True)

                if not projects.exists():
                    continue

                # If more than one project is found, match by the nearest
                # delta to the template date. This is not yet implemented.
                if projects.count() > 1:
                    logger.warn(f"Multiple candidate projects found for {name}")
                    continue

                project = projects.first()
                project.arcgis_item = item
                project.save()

                matches += 1

        return Response({"matches": matches})
