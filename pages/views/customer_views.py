import json

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from core.models import Territory
from customers.constants import Segment
from customers.models import Customer
from pages.forms.customers import CustomerForm

User = get_user_model()


class CustomerListView(ListView):
    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"

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
                    "label": "Segment",
                    "field": "segment",
                    "options": Segment.to_options(),
                },
            ]
        )


class CustomerDetailView(DetailView):
    model = Customer
    template_name = "customers/customer_detail.html"
    context_object_name = "customer"


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"

    def get_success_url(self):
        return reverse("customer-detail", kwargs={"pk": self.object.pk})


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"

    def get_success_url(self):
        return reverse("customer-detail", kwargs={"pk": self.object.pk})
