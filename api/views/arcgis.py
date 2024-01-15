import logging
import re

from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters.arcgis import ArcGISItemFilter
from api.serializers.arcgis import ArcGISItemSerializer
from repairs.models import Project
from third_party.arcgis.models import ArcGISItem

LOGGER = logging.getLogger(__name__)
RE_ITEM_TITLE = re.compile(r"^PSS\s+(?P<name>.*)\s+(?P<template_date>\d{6})$")


class ArcGISItemViewSet(ModelViewSet):
    """ArcGIS Item API view set"""

    queryset = ArcGISItem.objects.order_by("title")
    serializer_class = ArcGISItemSerializer
    filterset_class = ArcGISItemFilter

    def get_object(self):
        """Get an item by its pk or item_id"""
        pk = self.kwargs["pk"]
        queryset = self.get_queryset()

        if pk.isnumeric():
            return get_object_or_404(queryset, pk=pk)

        return get_object_or_404(queryset, item_id=pk)

    @action(methods=["GET", "POST"], detail=False)
    def match(self, request):
        """Match the ArcGIS web maps to a Project"""
        items = ArcGISItem.objects.filter(
            item_type=ArcGISItem.ItemType.WEB_MAP,
            title__startswith="PSS",
            projects__isnull=True,
        )

        matches = []

        for item in items:
            if match := RE_ITEM_TITLE.match(item.title):
                name = match.group("name")
                projects = Project.objects.filter(name=name, arcgis_item__isnull=True)

                if not projects.exists():
                    continue

                # If more than one project is found, match by the nearest
                # delta to the template date. This is not yet implemented.
                if projects.count() > 1:
                    LOGGER.warn(f"Multiple candidate projects found for {name}")
                    continue

                project = projects.first()
                project.arcgis_item = item
                project.save()

                matches.append({"id": project.id, "name": project.name})

        return Response({"count": len(matches), "matches": matches})
