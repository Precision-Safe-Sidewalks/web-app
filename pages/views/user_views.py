from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.views.generic import CreateView, ListView, UpdateView

from accounts.models import UserRole
from pages.forms.users import UserForm

User = get_user_model()


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"


class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = "users/user_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = UserRole.Role.choices
        return context

    def get_success_url(self):
        return reverse("user-list")


class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/user_form.html"
    context_object_name = "target_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = UserRole.Role.choices
        return context

    def get_success_url(self):
        return reverse("user-list")
