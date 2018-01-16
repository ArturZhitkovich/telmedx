from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (ListView, UpdateView, CreateView)

from .forms import AdminUserForm, AdminGroupForm

__all__ = (
    'TelmedxLoginView',
    'TelmedxAdminUsersUpdateView',
    'TelmedxAdminUsersListView',
    'TelmedxAdminUsersCreateView',
    'TelmedxGroupListView',
    'TelmedxGroupCreateView',
    'TelmedxGroupsUpdateView',
)

User = get_user_model()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/?next=%s' % request.path)

class BaseTelmedxMixin:
    """
    Mixin to add branding and other data
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = settings.INSTANCE_BRAND
        return context


class TelmedxLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super(TelmedxLoginView, self).get_context_data(**kwargs)
        # Add branding context
        context.update({'brand': settings.INSTANCE_BRAND})
        return context

    def get_redirect_url(self):
        # Check if user is an admin, go to the admin version
        return reverse_lazy('admin-users-list')


class TelmedxPaginatedListView(BaseTelmedxMixin, ListView):
    paginate_by = 15
    paginate_orphans = 5
    ordering_options = None


class TelmedxAdminUsersListView(TelmedxPaginatedListView):
    template_name = 'admin/users_list.html'
    model = User
    ordering_options = ('username', 'email', 'date_joined')

    def _flatten_options(self, options):
        return [item for sublist in options for item in sublist]

    def get_ordering(self, **kwargs):
        ordering = self.request.GET.get('sort', 'email_asc')
        ordered_options = map(lambda x: ['{}_asc'.format(x), '{}_desc'.format(x)], self.ordering_options)
        if ordering in self._flatten_options(ordered_options):
            if '_asc' in ordering:
                ordering = '{}'.format(ordering.split('_asc')[0])
            elif '_desc' in ordering:
                ordering = '-{}'.format(ordering.split('_desc')[0])
            return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.get_ordering()
        context['nsort'] = True if context['sort'] and context['sort'][0] == '-' else False
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            username_filter = Q(username__icontains=search)
            email_filter = Q(email__icontains=search)
            qs = qs.filter(username_filter | email_filter)

        return qs


class TelmedxAdminUsersUpdateView(BaseTelmedxMixin, UpdateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admin-users-list')


class TelmedxAdminUsersCreateView(BaseTelmedxMixin, CreateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admin-users-list')


class TelmedxGroupListView(TelmedxPaginatedListView):
    template_name = 'admin/groups_list.html'
    model = Group
    ordering_options = ('name',)


class TelmedxGroupCreateView(BaseTelmedxMixin, CreateView):
    template_name = 'admin/groups_create.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')


class TelmedxGroupsUpdateView(BaseTelmedxMixin, UpdateView):
    template_name = 'admin/users_update.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')
