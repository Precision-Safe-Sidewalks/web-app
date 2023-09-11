from django.shortcuts import get_object_or_404, reverse
from django.views.generic import CreateView, UpdateView

from customers.models import Contact, Customer
from pages.forms.contacts import ContactForm


class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contacts/contact_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["customer"] = self.kwargs["pk"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = get_object_or_404(Customer, pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return reverse("customer-detail", kwargs={"pk": self.kwargs["pk"]})


class ContactUpdateView(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = "contacts/contact_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.get_object().customer
        return context

    def get_success_url(self):
        customer = self.get_object().customer
        return reverse("customer-detail", kwargs={"pk": customer.pk})
