from rest_framework.routers import DefaultRouter

from api.views import measurements, tables

router = DefaultRouter()
router.register(
    "measurements", measurements.MeasurementViewSet, basename="measurements"
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


urlpatterns = router.urls
