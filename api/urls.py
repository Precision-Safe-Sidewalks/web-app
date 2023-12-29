from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import measurements, repairs, tables

router = DefaultRouter()

router.register(
    "measurements", measurements.MeasurementViewSet, basename="measurements"
)
router.register(
    "symbology",
    measurements.SymbologyViewSet,
    basename="symbology",
)
router.register(
    "tables/contacts",
    tables.ContactTableViewSet,
    basename="tables-contacts",
)
router.register(
    "tables/customers", tables.CustomerTableViewSet, basename="tables-customers"
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
    "pricing_sheet",
    repairs.PricingSheetViewSet,
    basename="documents-pricing-sheet",
)
router.register(
    "project_summary",
    repairs.ProjectSummaryViewSet,
    basename="documents-project-summary",
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
