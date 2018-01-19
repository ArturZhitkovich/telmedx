from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from .forms import AdminUserForm, AdminUserProfileForm
from .mixins import ProtectedTelmedxMixin, JSONResponseMixin
from .models import TelmedxProfile, TelmedxUser, TelmedxGroupProfile

__all__ = (
    'UserAndProfileFormView',
    'get_admin_group_form',
    'post_admin_group_form',
)

# type: TelmedxUser
User = get_user_model()


class ObjectAndProfileMixin:
    object = None
    object_profile = None

    def get_object(self, **kwargs):
        pass

    def get_object_profile(self, **kwargs):
        pass


class ObjectAndProfileFormView(ContextMixin, JSONResponseMixin,
                               TemplateResponseMixin, ObjectAndProfileMixin,
                               View):
    model = None
    profile_model = None
    model_form = None
    profile_form = None

    action_url = None
    success_url = None

    def get_action_url(self):
        if not self.action_url:
            raise ValueError('action_url must not be None or ',
                             'get_action_url must be overridden')
        return self.action_url

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {}

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, **kwargs):
        if getattr(self.model_form, 'is_bound', None):
            return self.model_form

        instance = kwargs.get('instance')
        return self.model_form(instance=instance, **self.get_form_kwargs())

    def get_profile_form(self, **kwargs):
        if getattr(self.profile_form, 'is_bound', None):
            return self.profile_form

        instance = kwargs.get('instance')
        return self.profile_form(instance=instance, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if kwargs.get('csrf'):
            context.update(csrf(self.request))

        context.update({
            'mode': kwargs.get('mode'),
            'form': self.get_form(instance=self.get_object()),
            'profile_form': self.get_profile_form(
                instance=self.get_object_profile()
            ),
            'action': self.get_action_url()
        })

        return context

    def get_object(self, pk=None, refresh=False):
        ret = self.object
        if (pk and refresh) or not ret:
            try:
                ret = self.model.objects.get(pk=pk)
                self.object = ret
            except self.model.DoesNotExist:
                ret = None

        return ret

    def get_object_profile(self):
        object = self.get_object()
        return getattr(object, 'profile', None)

    def form_valid(self, **kwargs):
        self.form = self.get_form(instance=kwargs.get('instance'))
        return self.form.is_valid()

    def profile_form_valid(self, **kwargs):
        instance = getattr(kwargs.get('instance'), 'profile')
        self.profile_form = self.get_profile_form(instance=instance)
        return self.profile_form.is_valid()

    def get(self, request, *args, **kwargs):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


class UserAndProfileFormView(ProtectedTelmedxMixin, ObjectAndProfileFormView):
    model = User
    model_form = AdminUserForm
    profile_model = TelmedxProfile
    profile_form = AdminUserProfileForm

    success_url = reverse_lazy('admin-users-list')
    template_name = 'admin/users_form.html'

    def get_data(self, context):
        pass

    def get_action_url(self):
        ret = reverse_lazy('admin-users-form')
        object = self.get_object()
        if object:
            ret = reverse_lazy('admin-users-update', kwargs={'pk': object.pk})
        return ret

    def get(self, request, *args, **kwargs):
        mode = request.GET.get('mode')
        user = self.get_object(pk=kwargs.get('pk'))

        if user and not getattr(user, 'profile', None):
            profile = self.profile_model()
            profile.user_id = user.pk
            profile.save()
            # Re-fetch user. Previous user won't have profile relation
            # user = self.get_object(pk=user.pk)

        kwargs['mode'] = mode
        kwargs['csrf'] = True

        return render_to_response(self.template_name,
                                  context=self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        kwargs['mode'] = 'update' if pk else 'create'
        kwargs['instance'] = self.get_object(pk=pk)

        if self.form_valid(**kwargs):
            obj = self.form.save()

            if self.profile_form_valid(**kwargs):
                profile = self.profile_form.save(commit=False)
                profile.user_id = obj.pk
                profile.save()

            if request.is_ajax():
                return self.render_to_json_response(
                    context=self.get_context_data(**kwargs)
                )
            else:
                return HttpResponseRedirect(self.success_url)

        errors = self.get_form().errors

        return errors


@csrf_protect
def get_admin_group_form(request):
    context = {}
    mode = request.GET.get('mode')
    try:
        gid = request.GET.get('gid')
        group = Group.objects.get(pk=gid)
    except Group.DoesNotExist:
        group = None

    if not getattr(group, 'profile', None):
        profile = TelmedxGroupProfile()
        profile.group_id = group.pk
        profile.save()
        group = Group.objects.get(id=gid)

    if group:
        context['profile_form'] = AdminUserProfileForm(instance=group.profile)
        context['user_form'] = AdminUserForm(instance=group)
        context['action'] = reverse_lazy('admin-groups-update', kwargs={'pk': group.pk})
    else:
        context['profile_form'] = AdminUserProfileForm()
        context['user_form'] = AdminUserForm(instance=TelmedxUser())
        context['action'] = reverse_lazy('admin-groups-create')


@csrf_protect
def post_admin_group_form(request):
    pass
