from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import (
    GroupAndProfileForm,
    UserAndProfileForm,
)
from .models import TelmedxProfile, TelmedxUser, TelmedxGroupProfile
from .serializers import TelmedxUserSerializer, TelmedxGroupSerializer

__all__ = (
    'ajax_group_form',
    'ajax_get_group_form',
    'ajax_post_group_form',
    'ajax_user_form',
)

# type: TelmedxUser
User = get_user_model()


def user_is_staff(user):
    """
    :param user:
    :type user: TelmedxUser
    :return:
    """
    return user.is_staff


def user_is_superuser(user):
    """
    :param user:
    :type user: TelmedxUser
    :return:
    """
    return user.is_superuser


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
            if 'logo' in form.files:
                profile.logo = form.files['logo']
            profile.save()
        else:
            group = Group()
            group.name = form.data['name']
            group.save()
            group.profile.contact_name = form.data['contact_name']
            group.profile.contact_email = form.data['contact_email']
            group.profile.contact_phone = form.data['contact_phone']
            if 'logo' in form.files:
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
    template_name = 'admin/groups_form.html'
    form = GroupAndProfileForm
    mode = kwargs.get('mode')
    action = reverse_lazy('admin-groups-update')
    group = None
    context = {}

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
        context.update({'instance': group})

    context.update({
        'mode': mode,
        'status_code': HTTPStatus.OK.value,
        'form': form,
        'action': action,
    })

    return render_to_response(template_name=template_name, context=context)


def ajax_delete_group_form(request, *args, **kwargs):
    pk = kwargs.get('pk')
    if pk:
        obj = Group.objects.get(pk=pk)
        obj.delete()

    return JsonResponse({'status': HTTPStatus.OK.value})


def ajax_get_user_form(request, mode=None, **kwargs):
    template_name = 'admin/users_form.html'
    form = UserAndProfileForm
    action = reverse_lazy('admin-users-update')
    user = None
    context = {}

    if mode == 'update':
        pk = kwargs.get('pk')
        if pk:
            user = User.objects.get(pk=pk)

        if user and not getattr(user, 'profile', None):
            # For a profile to be saved
            profile = TelmedxProfile()
            profile.user = user
            profile.save()
            # Re-fetch user. Previous user won't have profile relation
            # group = self.get_object(pk=user.pk)

        form = form(initial={
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'email': user.email,
            'username': user.username,
            'phone': user.profile.phone,
            'group': user.groups.first(),
        })
        action = reverse_lazy('admin-users-update', kwargs={'pk': user.pk})
        context.update({'instance': user})

    context.update({
        'mode': mode,
        'status_code': HTTPStatus.OK.value,
        'form': form,
        'action': action,
    })

    return render_to_response(template_name=template_name, context=context)


def ajax_post_user_form(request, **kwargs):
    form = UserAndProfileForm(request.POST, request.FILES)
    pk = kwargs.get('pk')
    serializer = TelmedxUserSerializer

    if form.is_valid():
        if pk:
            user = User.objects.get(pk=pk)
            user.email = form.data['email']
            user.username = form.data['username']
            user.save()
            profile = user.profile
            profile.first_name = form.data['first_name']
            profile.last_name = form.data['last_name']
            profile.phone = form.data['phone']
            profile.save()
        else:
            user = User()
            user.email = form.data['email']
            user.username = form.data['username']
            user.save()
            user.profile.first_name = form.data['first_name']
            user.profile.last_name = form.data['last_name']
            user.profile.phone = form.data['phone']
            user.profile.save()

        data = {
            'status_code': HTTPStatus.OK.value,
            'instance': serializer(instance=user).data,
            'html': render_to_string('admin/single_user_item.html',
                                     context={'user': user})
        }

        return JsonResponse(data=data)


def ajax_delete_user_form(request, *args, **kwargs):
    pk = kwargs.get('pk')
    if pk:
        obj = User.objects.get(pk=pk)
        obj.delete()

    return JsonResponse({'status': HTTPStatus.OK.value})


@require_http_methods(['GET', 'POST', 'DELETE'])
@login_required
@csrf_exempt
@user_passes_test(user_is_staff)
def ajax_user_form(request, *args, **kwargs):
    mode = request.GET.get('mode')

    if request.method == 'GET':
        return ajax_get_user_form(request, mode=mode, **kwargs)
    elif request.method == 'POST':
        return ajax_post_user_form(request, mode=mode, **kwargs)
    elif request.method == 'DELETE':
        return ajax_delete_user_form(request, mode=mode, **kwargs)


@user_passes_test(user_is_superuser)
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
