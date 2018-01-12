from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (ListView, UpdateView, CreateView)

from .forms import AdminUserForm, AdminGroupForm

__all__ = (
    'TelmedxLoginView',
    'TelmedxAdminUsersUpdateView',
    'TelmedxAdminUsersListView',
    'TelmedxGroupListView',
    'TelmedxGroupCreateView',
    'TelmedxGroupsUpdateView',
)

User = get_user_model()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)


class TelmedxLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super(TelmedxLoginView, self).get_context_data(**kwargs)
        # Add branding context
        context.update({'brand': settings.INSTANCE_BRAND})
        return context

    def get_redirect_url(self):
        # Check if user is an admin, go to the admin version
        return reverse_lazy('admin-users-list')


class TelmedxAdminUsersListView(ListView):
    template_name = 'admin/users_list.html'
    model = User


class TelmedxAdminUsersUpdateView(UpdateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admin-users-list')


class TelmedxGroupListView(ListView):
    template_name = 'admin/groups_list.html'
    model = Group


class TelmedxGroupCreateView(CreateView):
    template_name = 'admin/groups_create.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')


class TelmedxGroupsUpdateView(UpdateView):
    template_name = 'admin/users_update.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')

