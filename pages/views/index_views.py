import json

from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from core.models import Territory
from repairs.models import Project


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


