from django.urls import path

from pages.views import customer_views, index_views, map_views, project_views

urlpatterns = [
    path("customers/", customer_views.CustomerListView.as_view(), name="customer-list"),
    path(
        "customers/new/",
        customer_views.CustomerCreateView.as_view(),
        name="customer-create",
    ),
    path(
        "customers/<int:pk>/",
        customer_views.CustomerDetailView.as_view(),
        name="customer-detail",
    ),
    path(
        "customers/<int:pk>/edit/",
        customer_views.CustomerUpdateView.as_view(),
        name="customer-update",
    ),
    path(
        "customers/<int:pk>/projects/new/",
        project_views.ProjectCreateView.as_view(),
        name="customer-project-create",
    ),
    path("projects/", project_views.ProjectListView.as_view(), name="project-list"),
    path(
        "projects/<int:pk>/",
        project_views.ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "projects/<int:pk>/edit/",
        project_views.ProjectUpdateView.as_view(),
        name="project-update",
    ),
    path(
        "projects/<int:pk>/measurements/<str:stage>/",
        project_views.ProjectMeasurementsImportView.as_view(),
        name="project-measurements-import",
    ),
    path(
        "projects/<int:pk>/measurements/<str:stage>/export/",
        project_views.ProjectMeasurementsExportView.as_view(),
        name="project-measurements-export",
    ),
    path(
        "projects/<int:pk>/measurements/<str:stage>/clear/",
        project_views.ProjectMeasurementsClearView.as_view(),
        name="project-measurements-clear",
    ),
    path(
        "projects/<int:pk>/instructions/survey/",
        project_views.SurveyInstructionsView.as_view(),
        name="project-si",
    ),
    path(
        "projects/<int:pk>/instructions/project/",
        project_views.ProjectInstructionsView.as_view(),
        name="project-pi",
    ),
    path("map/", map_views.MapView.as_view(), name="map"),
    path("", index_views.IndexView.as_view(), name="index"),
]
