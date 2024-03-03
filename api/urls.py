from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import arcgis, measurements, repairs, tables

router = DefaultRouter()

router.register(
    "measurements", measurements.MeasurementViewSet, basename="measurements"
)
router.register(
    "symbology",
    measurements.SymbologyViewSet,
    basename="symbology",
)

# Datatables API views
router.register(
    "tables/contacts",
    tables.ContactTableViewSet,
    basename="tables-contacts",
)
router.register(
    "tables/customers",
    tables.CustomerTableViewSet,
    basename="tables-customers",
)
router.register(
    "tables/projects",
    tables.ProjectTableViewSet,
    basename="tables-projects",
)
router.register(
    "tables/users",
    tables.UserTableViewSet,
    basename="tables-users",
)
router.register(
    "tables/dashboard",
    tables.DashboardTableViewSet,
    basename="tables-dashboard",
)

# Project API views
router.register(
    "projects/layers",
    repairs.ProjectLayerViewSet,
    basename="project-layers",
)
router.register(
    "projects",
    repairs.ProjectViewSet,
    basename="projects",
)
router.register(
    "pricing_sheet",
    repairs.PricingSheetViewSet,
    basename="documents-pricing-sheet",
)
router.register(
    "project_summary",
    repairs.ProjectSummaryViewSet,
    basename="documents-project-summary",
)

# ArcGIS API views
router.register(
    "arcgis/items",
    arcgis.ArcGISItemViewSet,
    basename="arcgis_items",
)

urlpatterns = router.urls + [
    path(
        "documents/instructions/survey/<int:pk>/",
        repairs.SurveyInstructionsAPIView.as_view(),
        name="documents-survey-instructions",
    ),
    path(
        "documents/instructions/project/<int:pk>/",
        repairs.ProjectInstructionsAPIView.as_view(),
        name="documents-project-instructions",
    ),
]
