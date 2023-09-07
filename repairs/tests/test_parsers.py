import unittest

from repairs.parsers import ProductionMeasurement, SurveyMeasurement


class TestMeasurementParsers(unittest.TestCase):
    """Unit tests for parsing measurement files"""

    def test_parse_survey_measurements_csv(self):
        """Test parsing a survey measurements CSV file"""

        filename = "repairs/tests/fixtures/survey_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            measurements = SurveyMeasurement.from_csv(f)
            self.assertEqual(len(measurements), 165)

    def test_parse_production_measurements_csv(self):
        """Test parsing a production measurements CSV file"""

        filename = "repairs/tests/fixtures/production_template.csv"

        with open(filename, "r", encoding="utf-8-sig") as f:
            measurements = ProductionMeasurement.from_csv(f)
            self.assertEqual(len(measurements), 59)
