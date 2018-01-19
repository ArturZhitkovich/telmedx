from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect

from .forms import AdminUserForm, AdminGroupForm, AdminUserProfileForm
from .mixins import *
from .models import TelmedxUser

__all__ = (
    'TelmedxLoginView',
    'TelmedxAdminUsersUpdateView',
    'TelmedxAdminUsersListView',
    'TelmedxAdminUsersCreateView',
    'TelmedxAdminUsersDeleteView',
    'TelmedxGroupListView',
    'TelmedxGroupCreateView',
    'TelmedxGroupsUpdateView',

    'get_admin_user_form',
    'post_admin_user_form',
    'get_admin_group_form',
    'post_admin_group_form',
)

# type: TelmedxUser
User = get_user_model()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class TelmedxLoginView(BaseTelmedxMixin, LoginView):
    redirect_authenticated_user = True

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


def post_admin_user_form(request, pk=None):
    context = {'brand': settings.INSTANCE_BRAND}

    template_name = 'admin/users_update.html'
    success_url = reverse_lazy('admin-users-list')

    if request.method == 'POST':
        if pk:
            context['mode'] = 'update'
            user = User.objects.get(pk=pk)
            user_form = AdminUserForm(data=request.POST, instance=user)
            profile_form = AdminUserProfileForm(data=request.POST,
                                                instance=user.profile)
        else:
            context['mode'] = 'create'
            user_form = AdminUserForm(data=request.POST)
            profile_form = AdminUserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save()

            if request.is_ajax():
                return JsonResponse({
                    'status': 'OK',
                    'data': {}
                })
            else:
                return HttpResponseRedirect(success_url)

        context['user_form'] = user_form
        context['profile_form'] = profile_form
        context['user_form_errors'] = user_form.errors
        context['profile_form_errors'] = profile_form.errors

        if request.is_ajax():
            return JsonResponse({
                'status': 'ERROR',
                'data': {
                    'user_form_errors': user_form.errors,
                    'profile_form_errors': profile_form.errors,
                }
            }, status=HTTPStatus.BAD_REQUEST.value)
        else:
            return render_to_response(template_name, context)
    # return HttpResponseRedirect(back_url)


@csrf_protect
def get_admin_user_form(request):
    context = {}
    mode = request.GET.get('mode')
    try:
        uid = request.GET.get('uid')
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        user = None

    if user:
        context['profile_form'] = AdminUserProfileForm(instance=user.profile)
        context['user_form'] = AdminUserForm(instance=user)
        context['action'] = reverse_lazy('admin-users-update', kwargs={'pk': user.pk})
    else:
        context['profile_form'] = AdminUserProfileForm()
        context['user_form'] = AdminUserForm(instance=TelmedxUser())
        context['action'] = reverse_lazy('admin-users-create')

    context['mode'] = mode
    context.update(csrf(request))

    return render_to_response('admin/users_form.html', context)


@csrf_protect
def get_admin_group_form(request):
    pass


@csrf_protect
def post_admin_group_form(request):
    pass
