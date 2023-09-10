from lib.test_helpers import IntegrationTestBase
from repairs.factories import ProjectFactory
from repairs.models import Measurement
from repairs.models.constants import Stage


class TestMeasurement(IntegrationTestBase):
    """Unit/integration tests for the Measurement model"""

    def test_import_from_csv_survey(self):
        """Test importing the survey measurements from CSV"""

        project = ProjectFactory()
        stage = Stage.SURVEY

        filename = "repairs/tests/fixtures/survey_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            measurements = Measurement.import_from_csv(f, project, stage)
            self.assertEqual(measurements.count(), 165)

    def test_import_from_csv_production(self):
        """Test importint the production measurements from CSV"""

        project = ProjectFactory()
        stage = Stage.PRODUCTION

        filename = "repairs/tests/fixtures/production_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            measurements = Measurement.import_from_csv(f, project, stage)
            self.assertEqual(measurements.count(), 59)
