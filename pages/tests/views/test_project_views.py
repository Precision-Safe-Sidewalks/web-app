from django.shortcuts import reverse

from core.factories import TerritoryFactory
from customers.factories import ContactFactory, CustomerFactory
from lib.test_helpers import IntegrationTestBase
from repairs.factories import ProjectFactory
from repairs.models import Measurement


class TestProjectListView(IntegrationTestBase):
    """Unit tests for the project list view"""

    def test_list(self):
        customer = CustomerFactory()
        ProjectFactory.create_batch(5, customer=customer)
        url = reverse("project-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_list_paginated(self):
        customer = CustomerFactory()
        ProjectFactory.create_batch(15, customer=customer)
        url = reverse("project-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class TestProjectDetailView(IntegrationTestBase):
    """Unit tests for the project detail view"""

    def test_detail(self):
        project = ProjectFactory()
        url = reverse("project-detail", kwargs={"pk": project.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class TestProjectCreateView(IntegrationTestBase):
    """Unit tests for the project create view"""

    def test_create(self):
        customer = CustomerFactory()
        territory = TerritoryFactory()
        contact = ContactFactory(customer=customer)

        data = {
            "customer": customer.pk,
            "name": "Test project",
            "address": "101 Main St.",
            "business_development_manager": self.bdm.pk,
            "territory": territory.pk,
            "primary_contact": contact.pk,
            "pricing_model": 1,
        }

        url = reverse("customer-project-create", kwargs={"pk": customer.pk})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(customer.projects.count(), 1)


class TestProjectUpdateView(IntegrationTestBase):
    """Unit tests for the project update views"""

    def test_update(self):
        project = ProjectFactory()
        contact = ContactFactory(customer=project.customer)

        data = {
            "customer": project.customer.pk,
            "name": "Test project",
            "address": "",
            "business_development_manager": self.bdm.pk,
            "territory": project.territory.pk,
            "primary_contact": contact.pk,
            "pricing_model": project.pricing_model,
        }

        url = reverse("project-update", kwargs={"pk": project.pk})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)

        project.refresh_from_db()
        self.assertEqual(project.name, data["name"])
        self.assertEqual(project.primary_contact, contact)

    def test_update_status(self):
        project = ProjectFactory(status=1)

        data = {
            "status": 2,
        }

        url = reverse("project-update-status", kwargs={"pk": project.pk})
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)

        project.refresh_from_db()
        self.assertEqual(project.status, data["status"])


class TestProjectMeasurementsImportView(IntegrationTestBase):
    """Unit tests for the measurement import view"""

    def test_import_survey(self):
        project = ProjectFactory()

        filename = "repairs/tests/fixtures/survey_template.csv"
        url = reverse(
            "project-measurements-import", kwargs={"pk": project.pk, "stage": "survey"}
        )

        with open(filename, "rb") as f:
            data = {"file": f}
            resp = self.client.post(url, data)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(project.measurements.count(), 165)

    def test_import_production(self):
        project = ProjectFactory()

        filename = "repairs/tests/fixtures/production_template.csv"
        url = reverse(
            "project-measurements-import",
            kwargs={"pk": project.pk, "stage": "production"},
        )

        with open(filename, "rb") as f:
            data = {"file": f}
            resp = self.client.post(url, data)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(project.measurements.count(), 59)


class TestProjectMeasurementsExportView(IntegrationTestBase):
    """Unit tests for the measurement export view"""

    def test_export_survey(self):
        project = ProjectFactory()
        filename = "repairs/tests/fixtures/survey_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            Measurement.import_from_csv(f, project, "SURVEY")
            self.assertEqual(project.measurements.count(), 165)

        url = reverse(
            "project-measurements-export", kwargs={"pk": project.pk, "stage": "survey"}
        )
        resp = self.client.get(url)

        data = resp.content.decode("utf-8").strip().split("\n")
        self.assertEqual(len(data), 166)  # 165 measurements + header

    def test_export_production(self):
        project = ProjectFactory()
        filename = "repairs/tests/fixtures/production_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            Measurement.import_from_csv(f, project, "PRODUCTION")
            self.assertEqual(project.measurements.count(), 59)

        url = reverse(
            "project-measurements-export",
            kwargs={"pk": project.pk, "stage": "production"},
        )
        resp = self.client.get(url)

        data = resp.content.decode("utf-8").strip().split("\n")
        self.assertEqual(len(data), 60)  # 59 measurements + header


class TestMeasurementClearView(IntegrationTestBase):
    """Unit tests for the measurement clear view"""

    def test_clear(self):
        project = ProjectFactory()
        filename = "repairs/tests/fixtures/survey_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            Measurement.import_from_csv(f, project, "SURVEY")
            self.assertEqual(project.measurements.count(), 165)

        url = reverse(
            "project-measurements-clear", kwargs={"pk": project.pk, "stage": "survey"}
        )
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(project.measurements.count(), 0)

    def test_clear_no_measurements(self):
        project = ProjectFactory()
        self.assertEqual(project.measurements.count(), 0)

        url = reverse(
            "project-measurements-clear", kwargs={"pk": project.pk, "stage": "survey"}
        )
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(project.measurements.count(), 0)


class TestSurveyInstructionsView(IntegrationTestBase):
    """Unit tests for the survey instructions view"""

    def test_defaults(self):
        """Test saving only the required data"""
        project = ProjectFactory()

        url = reverse("project-si", kwargs={"pk": project.pk})
        redirect_url = reverse("project-detail", kwargs={"pk": project.pk})
        data = {}

        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, redirect_url)


class TestProjectInstructionsView(IntegrationTestBase):
    """Unit tests for the project instructions view"""

    def test_defaults(self):
        """Test saving only the required data"""
        project = ProjectFactory()

        url = reverse("project-pi", kwargs={"pk": project.pk})
        redirect_url = reverse("project-detail", kwargs={"pk": project.pk})
        data = {}

        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, redirect_url)
