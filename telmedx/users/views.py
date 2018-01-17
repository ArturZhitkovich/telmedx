from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect

from .forms import AdminUserForm, AdminGroupForm
from .mixins import *

__all__ = (
    'TelmedxLoginView',
    'TelmedxAdminUsersUpdateView',
    'TelmedxAdminUsersListView',
    'TelmedxAdminUsersCreateView',
    'TelmedxGroupListView',
    'TelmedxGroupCreateView',
    'TelmedxGroupsUpdateView',

    'get_admin_form',
)

# @type TelmedxUser
User = get_user_model()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class TelmedxLoginView(LoginView):
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add branding context
        context.update({'brand': settings.INSTANCE_BRAND})
        return context

    def get_redirect_url(self):
        ret = reverse_lazy('device-home')
        if self.request.user.is_staff:
            ret = reverse_lazy('admin-users-list')
        return ret


class TelmedxAdminUsersListView(TelmedxPaginatedListView):
    template_name = 'admin/users_list.html'
    model = User
    ordering_options = (
        'profile__first_name',
        'profile__last_name',
        'username',
        'email',
        'date_joined'
    )

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
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            username_filter = Q(username__icontains=search)
            first_name_filter = Q(profile__first_name__icontains=search)
            last_name_filter = Q(profile__last_name__icontains=search)
            email_filter = Q(email__icontains=search)
            qs = qs.filter(username_filter |
                           email_filter |
                           first_name_filter |
                           last_name_filter)

        return qs


class TelmedxAdminUsersUpdateView(TelmedxUpdateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admin-users-list')
    back_url = reverse_lazy('admin-users-list')


class TelmedxAdminUsersCreateView(TelmedxCreateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admin-users-list')
    back_url = reverse_lazy('admin-users-list')


class TelmedxGroupListView(TelmedxPaginatedListView):
    template_name = 'admin/groups_list.html'
    model = Group
    ordering_options = ('name',)


class TelmedxGroupCreateView(TelmedxCreateView):
    template_name = 'admin/groups_create.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')
    back_url = reverse_lazy('admin-groups-list')


class TelmedxGroupsUpdateView(TelmedxUpdateView):
    template_name = 'admin/groups_create.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')
    back_url = reverse_lazy('admin-groups-list')


@csrf_protect
def get_admin_form(request):
    context = {}
    try:
        uid = request.GET.get('uid')
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        user = None
    except Exception as e:
        print(e)

    if user:
        form = AdminUserForm(instance=user)
        context['form'] = form
        context['mode'] = 'edit'
        context['action'] = reverse_lazy('admin-users-update', kwargs={'pk': user.pk})
        context.update(csrf(request))

    return render_to_response('admin/users_form.html', context)
