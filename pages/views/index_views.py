from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Index page template view"""

    template_name = "index/index.html"
