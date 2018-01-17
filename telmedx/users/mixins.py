from django.conf import settings
from django.views.generic import (ListView, UpdateView, CreateView)

__all__ = (
    'BaseTelmedxMixin',
    'TelmedxPaginatedListView',
    'TelmedxUpdateView',
    'TelmedxCreateView',
)


class BaseTelmedxMixin:
    """
    Mixin to add branding and other data
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = settings.INSTANCE_BRAND
        return context


class TelmedxPaginatedListView(BaseTelmedxMixin, ListView):
    paginate_by = 15
    paginate_orphans = 5
    ordering_options = None


class TelmedxUpdateView(BaseTelmedxMixin, UpdateView):
    back_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'edit'
        context['back_url'] = self.back_url
        return context


class TelmedxCreateView(BaseTelmedxMixin, CreateView):
    back_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'create'
        context['back_url'] = self.back_url
        return context
