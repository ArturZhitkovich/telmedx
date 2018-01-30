from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DeleteView
)
from django.views.generic.base import ContextMixin

__all__ = (
    'BaseTelmedxMixin',
    'ProtectedTelmedxMixin',
    'TelmedxPaginatedListView',
    'TelmedxUpdateView',
    'TelmedxCreateView',
    'TelmedxDeleteView',
)


class BaseTelmedxMixin(ContextMixin):
    """
    Mixin to add branding and other data
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = settings.INSTANCE_BRAND
        return context


class JSONResponseMixin:
    def render_to_json_response(self, context, **kwargs):
        data = self.get_data(context)
        if data.get('errors'):
            data.update({'status_code': HTTPStatus.BAD_REQUEST.value})
        else:
            data.update({'status_code': HTTPStatus.OK.value})

        return JsonResponse(data, **kwargs)

    def get_data(self, context):
        """
        Should be overridden to handle changing data to a serializable format.
        :param context:
        :return:
        """
        return context


class ObjectAndProfileMixin:
    object = None
    object_profile = None

    def get_object(self, **kwargs):
        pass

    def get_object_profile(self, **kwargs):
        pass


class ProtectedTelmedxMixin(UserPassesTestMixin, BaseTelmedxMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class TelmedxPaginatedListView(ProtectedTelmedxMixin, ListView):
    paginate_by = 15
    paginate_orphans = 5
    ordering_options = None


class TelmedxUpdateView(ProtectedTelmedxMixin, UpdateView):
    back_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'edit'
        context['back_url'] = self.back_url
        return context

    def post(self, request, *args, **kwargs):
        # Check if user is allowed to update this user
        allowed = False
        if request.user.is_superuser:
            allowed = True
        elif request.user.is_staff:
            allowed = True

        return allowed


class TelmedxCreateView(ProtectedTelmedxMixin, CreateView):
    back_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'create'
        context['back_url'] = self.back_url
        return context


class TelmedxDeleteView(ProtectedTelmedxMixin, DeleteView):
    back_url = None
