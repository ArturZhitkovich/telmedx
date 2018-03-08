from http import HTTPStatus

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .forms import AdminUserForm, AdminGroupForm, AdminUserProfileForm
from .mixins import *
from .models import TelmedxUser
from .serializers import *

__all__ = (
    'TelmedxLoginView',
    'TelmedxAdminUsersUpdateView',
    'TelmedxAdminUsersListView',
    'TelmedxAdminUsersCreateView',
    'TelmedxAdminUsersDeleteView',
    'TelmedxGroupListView',
    'TelmedxGroupCreateView',
    'TelmedxGroupsUpdateView',
    'TelmedxErrorView',
)

# type: TelmedxUser
User = get_user_model()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class TelmedxLoginView(BaseTelmedxMixin, LoginView):
    redirect_authenticated_user = True

    def get_redirect_url(self):
        # TODO: Don't allow normal users to login?
        ret = reverse_lazy('user-denied')
        if self.request.user.is_superuser:
            ret = reverse_lazy('admin-groups-list')
        elif self.request.user.is_staff:
            ret = reverse_lazy('admin-users-list')
        return ret


class TelmedxAdminUsersListView(TelmedxPaginatedListView):
    template_name = 'admin/users_list.html'
    model = User
    ordering_options = (
        'profile__first_name',
        'profile__last_name',
        'email',
        'date_joined',
        'groups',
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
        context['groups'] = Group.objects.all()
        return context

    def _get_search_filter(self, search):
        """
        Generate a search query with `Q` objects with `search` param
        :param search:
        :return:
        """
        username_filter = Q(username__icontains=search)
        first_name_filter = Q(profile__first_name__icontains=search)
        last_name_filter = Q(profile__last_name__icontains=search)
        email_filter = Q(email__icontains=search)
        return Q(username_filter |
                 email_filter |
                 first_name_filter |
                 last_name_filter)

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        user_type = self.request.GET.get('utype')
        user_group = self.request.GET.get('ugroup')
        user = self.request.user

        if user.is_staff and not user.is_superuser:
            # Filter users that belong into the current user's group(s)
            # Also, do not show any superusers for normal admins.
            qs = qs.filter(groups__in=user.groups.all(),
                           is_superuser=False)

        if user_type:
            if user_type == 'mobile':
                qs = qs.filter(is_superuser=False, is_staff=False)
            elif user_type == 'admin':
                qs = qs.filter(is_superuser=False, is_staff=True)

        if user_group:
            # Only superusers should be able to see this
            if user.is_superuser and user_group != 'all':
                qs = qs.filter(groups__pk=int(user_group))

        if search:
            qs = qs.filter(self._get_search_filter(search))

        return qs


class TelmedxAdminUsersUpdateView(TelmedxUpdateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    next_form_class = AdminUserProfileForm
    success_url = reverse_lazy('admin-users-list')
    back_url = reverse_lazy('admin-users-list')


class TelmedxAdminUsersCreateView(TelmedxCreateView):
    template_name = 'admin/users_update.html'
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admin-users-list')
    back_url = reverse_lazy('admin-users-list')


class TelmedxAdminUsersDeleteView(TelmedxDeleteView):
    model = User
    success_url = reverse_lazy('admin-users-list')
    back_url = reverse_lazy('admin-groups-list')

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.pk == int(kwargs.get('pk')):
            raise ValidationError(
                'Cannot delete same user as current user.',
                code=HTTPStatus.BAD_REQUEST.value
            )

        return super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if self.request.is_ajax():
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({
                'status': 'OK',
                'data': {}
            })
        return super().delete(request, *args, **kwargs)


class TelmedxGroupListView(TelmedxPaginatedListView):
    template_name = 'admin/groups_list.html'
    model = Group
    ordering_options = (
        'name',
        'profile__contact_name',
        'profile__mobile_users',
        'profile__date_created',
    )

    def test_func(self):
        return self.request.user.is_superuser

    def _flatten_options(self, options):
        return [item for sublist in options for item in sublist]

    def get_ordering(self, **kwargs):
        ordering = self.request.GET.get('sort', 'name_asc')
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
        context['groups'] = Group.objects.all()
        return context

    def _get_search_filter(self, search):
        """
        Generate a search query with `Q` objects with `search` param
        :param search:
        :return:
        """
        name_filter = Q(name__icontains=search)
        contact_filter = Q(profile__contact__icontains=search)
        return Q(name_filter | contact_filter)

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')

        if search:
            qs = qs.filter(self._get_search_filter(search))

        return qs


class TelmedxGroupCreateView(TelmedxCreateView):
    template_name = 'admin/groups_create.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')
    back_url = reverse_lazy('admin-groups-list')

    def test_func(self):
        return self.request.user.is_superuser


class TelmedxGroupsUpdateView(TelmedxUpdateView):
    template_name = 'admin/groups_create.html'
    model = Group
    form_class = AdminGroupForm
    success_url = reverse_lazy('admin-groups-list')
    back_url = reverse_lazy('admin-groups-list')

    def test_func(self):
        return self.request.user.is_superuser


class TelmedxErrorView(BaseTelmedxMixin, TemplateView):
    template_name = 'admin/error_denied.html'

