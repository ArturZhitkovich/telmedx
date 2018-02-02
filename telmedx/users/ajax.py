from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from .forms import (
    AdminUserForm,
    AdminUserProfileForm,
    AdminGroupForm,
    AdminGroupProfileForm,
    GroupAndProfileForm,
)
from .mixins import (
    ProtectedTelmedxMixin,
    JSONResponseMixin,
    ObjectAndProfileMixin
)
from .models import TelmedxProfile, TelmedxUser, TelmedxGroupProfile
from .serializers import TelmedxUserSerializer, TelmedxGroupSerializer

__all__ = (
    'UserAndProfileFormView',
    'GroupAndProfileFormView',
    'ajax_group_form',
    'ajax_get_group_form',
    'ajax_post_group_form',
)

# type: TelmedxUser
User = get_user_model()


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
        kwargs = {
            'user': self.request.user,
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, **kwargs):
        # If the form is bound (has existing, submitted data) return it,
        # otherwise, prepopulate it with the instance in the kwargs
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
        instance = getattr(kwargs.get('instance'), 'profile', None)
        self.profile_form = self.get_profile_form(instance=instance)
        return self.profile_form.is_valid()

    def _can_edit_user(self, request, instance):
        """
        :param request:
        :param instance:
        :type instance: TelmedxUser|Group
        :return:
        :rtype: bool
        """
        user = self.request.user
        has_group = False
        if user.is_superuser:
            has_group = True
        elif user.is_staff:
            instance_groups = instance.groups.all()
            for g in user.groups.all():
                if g in instance_groups:
                    has_group = True
                    break
        return has_group

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
        """
        Get data for use in JSONResponse
        :param context:
        :return:
        """
        instance = context.get('instance')
        form = context.get('form')

        serializer = TelmedxUserSerializer(instance)
        data = {'instance': serializer.data}

        if form and form.errors:
            data.update({'errors': str(form.errors)})

        return data

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
        mode = kwargs['mode'] = 'update' if pk else 'create'
        instance = kwargs['instance'] = self.get_object(pk=pk)

        if mode == 'update':
            if not self._can_edit_user(request, kwargs['instance']):
                raise PermissionDenied('You cannot update this user.')
        elif mode == 'create':
            pass
            # if not self._can_create(request, kwargs['instance']):
            #     raise PermissionDenied('You cannot create this user.')

        if self.form_valid(**kwargs):
            obj = self.form.save()

            # Rewrite instance kwarg since the initial cration of the
            # obj will automatically create a profile instance.
            if not pk:
                kwargs['instance'] = obj

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

        return self.render_to_json_response(context={
            'form': self.form,
        })


class GroupAndProfileFormView(ProtectedTelmedxMixin, ObjectAndProfileFormView):
    model = Group
    model_form = AdminGroupForm
    profile_model = TelmedxGroupProfile
    profile_form = AdminGroupProfileForm

    success_url = reverse_lazy('admin-groups-list')
    template_name = 'admin/groups_form.html'

    def get_data(self, context):
        instance = context.get('instance')
        form = context.get('form')

        serializer = TelmedxGroupSerializer(instance)
        data = {'instance': serializer.data}

        if form and form.errors:
            data.update({'errors': str(form.errors)})

        return data

    def get_action_url(self):
        ret = reverse_lazy('admin-groups-form')
        object = self.get_object()
        if object:
            ret = reverse_lazy('admin-groups-update', kwargs={'pk': object.pk})
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

            # Rewrite instance kwarg since the initial cration of the
            # obj will automatically create a profile instance.
            if not pk:
                kwargs['instance'] = obj

            if self.profile_form_valid(**kwargs):
                profile = self.profile_form.save(commit=False)
                profile.group_id = obj.pk
                profile.save()

            if request.is_ajax():
                return self.render_to_json_response(
                    context=self.get_context_data(**kwargs)
                )
            else:
                return HttpResponseRedirect(self.success_url)

        return self.render_to_json_response(context={
            'form': self.form,
        })


def ajax_post_group_form(request, **kwargs):
    form = GroupAndProfileForm(request.POST, request.FILES)
    pk = kwargs.get('pk')
    serializer = TelmedxGroupSerializer

    if form.is_valid():
        if pk:
            group = Group.objects.get(pk=pk)
            group.name = form.data['name']
            group.save()
            profile = group.profile
            profile.contact_name = form.data['contact_name']
            profile.contact_email = form.data['contact_email']
            profile.contact_phone = form.data['contact_phone']
            profile.logo = form.files['logo']
            profile.save()
        else:
            group = Group()
            group.name = form.data['name']
            group.save()
            group.profile.contact_name = form.data['contact_name']
            group.profile.contact_email = form.data['contact_email']
            group.profile.contact_phone = form.data['contact_phone']
            group.profile.logo = form.files['logo']
            group.profile.save()

        data = {
            'status_code': HTTPStatus.OK.value,
            'instance': serializer(instance=group).data,
            'html': render_to_string('admin/single_group_item.html',
                                     context={'group': group})
        }

        return JsonResponse(data=data)


def ajax_get_group_form(request, **kwargs):
    template_name = 'admin/gp_form.html'
    form = GroupAndProfileForm
    mode = kwargs.get('mode')
    action = reverse_lazy('admin-groups-update')
    group = None

    if mode == 'update':
        pk = kwargs.get('pk')
        if pk:
            group = Group.objects.get(pk=pk)

        if group and not getattr(group, 'profile', None):
            # For a profile to be saved
            profile = TelmedxGroupProfile()
            profile.group = group.pk
            profile.save()
            # Re-fetch user. Previous user won't have profile relation
            # group = self.get_object(pk=user.pk)

        form = form(initial={
            'contact_email': group.profile.contact_email,
            'contact_name': group.profile.contact_name,
            'contact_phone': group.profile.contact_phone,
            'logo': group.profile.logo,
            'name': group.name
        })
        action = reverse_lazy('admin-groups-update', kwargs={'pk': group.pk})

    context = {
        'mode': mode,
        'status_code': HTTPStatus.OK.value,
        'form': form,
        'action': action,
    }

    return render_to_response(template_name=template_name, context=context)


def ajax_delete_group_form(request, *args, **kwargs):
    pk = kwargs.get('pk')
    if pk:
        obj = Group.objects.get(pk=pk)
        obj.delete()

    return JsonResponse({'status': HTTPStatus.OK.value})


@require_http_methods(['GET', 'POST', 'DELETE'])
@login_required
@csrf_exempt
def ajax_group_form(request, *args, **kwargs):
    mode = request.GET.get('mode')

    if request.method == 'GET':
        return ajax_get_group_form(request, mode=mode, **kwargs)
    elif request.method == 'POST':
        return ajax_post_group_form(request, mode=mode, **kwargs)
    elif request.method == 'DELETE':
        return ajax_delete_group_form(request, mode=mode, **kwargs)
