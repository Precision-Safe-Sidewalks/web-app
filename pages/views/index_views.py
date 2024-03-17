import json
from datetime import date

from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from core.models import Territory
from lib.pay_periods import get_pay_periods
from repairs.models import Measurement, Project

User = get_user_model()


class IndexView(TemplateView):
    """Index page template view"""

    template_name = "index/index.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["table_filters"] = self.get_table_filters()
        return context

    def get_table_filters(self):
        """Return the JSON list of table filter options dictionaries"""
        return json.dumps(
            [
                {
                    "label": "BD",
                    "field": "business_development_manager",
                    "options": User.bdm.to_options(),
                },
                {
                    "label": "Territory",
                    "field": "territory",
                    "options": Territory.to_options(),
                },
                {
                    "label": "Stage",
                    "field": "status",
                    "options": Project.Status.to_options(),
                    "default": [Project.Status.SCHEDULED],
                },
            ]
        )


class TechProductionDashboard(TemplateView):
    """Tech production dashboard view"""

    template_name = "dashboards/tech_production.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["table_filters"] = self.get_table_filters()
        return context

    def get_table_filters(self):
        """Return the JSON list of table filter ooptions dictionaries"""
        min_date = date(2024, 1, 1)
        max_date = date.today()
        periods = get_pay_periods(min_date, max_date)[::-1]

        techs = (
            Measurement.objects.filter(tech__isnull=False)
            .values_list("tech", flat=True)
            .distinct()
        )
        techs = [{"key": tech, "value": tech} for tech in sorted(techs)]

        return json.dumps(
            [
                {
                    "label": "Pay Period",
                    "field": "period",
                    "options": periods,
                    "multiple": False,
                    "default": [periods[0]["key"]],
                },
                {
                    "label": "Tech",
                    "field": "tech",
                    "options": techs,
                    "multiple": True,
                },
            ]
        )
