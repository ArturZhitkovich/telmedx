from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DeleteView
)

__all__ = (
    'BaseTelmedxMixin',
    'ProtectedTelmedxMixin',
    'TelmedxPaginatedListView',
    'TelmedxUpdateView',
    'TelmedxCreateView',
    'TelmedxDeleteView',
)


class BaseTelmedxMixin:
    """
    Mixin to add branding and other data
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = settings.INSTANCE_BRAND
        return context


class ProtectedTelmedxMixin(UserPassesTestMixin, BaseTelmedxMixin):
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


class TelmedxCreateView(ProtectedTelmedxMixin, CreateView):
    back_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'create'
        context['back_url'] = self.back_url
        return context


class TelmedxDeleteView(ProtectedTelmedxMixin, DeleteView):
    back_url = None
