# Create your views here.
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, ExpressionWrapper, DurationField
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.views.generic import ListView

from ttux.models import MobileCam, sessionLog
from usage.utils import export_usage_csv
from users.views import ProtectedTelmedxMixin

User = get_user_model()


@login_required
def home(request):
    logs = sessionLog.objects.filter(device__groups=request.user.groups.all())
    paginator = Paginator(logs, 25)  # Show 25 contacts per page

    page = request.GET.get('page')

    if request.GET.get('export_last_week', None) is not None:
        try:
            device = MobileCam.objects.filter(groups=request.user.groups.all).get(name=request.GET.get('device'))
            logs.filter(device=device)
        except MobileCam.DoesNotExist:
            pass
        logs = logs.filter(begin_timestamp__gt=datetime.datetime.now() - datetime.timedelta(days=7))
        return export_usage_csv(logs)

    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        logs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        logs = paginator.page(paginator.num_pages)

    return render_to_response('admin/usage.html', context={
        'records': logs,
        'brand': settings.INSTANCE_BRAND,
        'request': request,
    })


class UsageGroupView(ProtectedTelmedxMixin, ListView):
    model = sessionLog
    queryset = sessionLog.objects.all()
    template_name = 'admin/usage.html'
    ordering_options = (
        'device__user',
        'begin_timestamp',
        'frames',
        'captured_images',
        'q_duration'
    )

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        qs = qs.filter(device__user__groups__id=self.kwargs.get('pk'))

        # Use F-expressions to annotate a duration directly on the query
        # Allows this field to be orderable in the `get_ordering` method.
        qs = qs.annotate(
            q_duration=ExpressionWrapper(
                F('end_timestamp') - F('begin_timestamp'),
                output_field=DurationField()
            )
        )
        return qs

    def _flatten_options(self, options):
        return [item for sublist in options for item in sublist]

    def get_ordering(self, **kwargs):
        ordering = self.request.GET.get('sort', 'begin_timestamp')
        ordered_options = map(lambda x: ['{}_asc'.format(x), '{}_desc'.format(x)], self.ordering_options)
        if ordering in self._flatten_options(ordered_options):
            if '_asc' in ordering:
                ordering = '{}'.format(ordering.split('_asc')[0])
            elif '_desc' in ordering:
                ordering = '-{}'.format(ordering.split('_desc')[0])

            # if 'user' in ordering:
            #     ordering = ordering.replace('user', 'device__user')
            return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.get_ordering(**kwargs)
        context['group'] = get_object_or_404(Group, pk=self.kwargs.get('pk'))
        return context


@login_required
def group_view(request, pk=None):
    group = get_object_or_404(Group, pk=pk)

    logs = sessionLog.objects.filter(device__user__groups=group)

    if request.GET.get('export_last_week', None) is not None:
        logs = logs.filter(begin_timestamp__gt=datetime.datetime.now() - datetime.timedelta(days=7))
        return export_usage_csv(logs)

    paginator = Paginator(logs, 25)

    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        logs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        logs = paginator.page(paginator.num_pages)

    return render_to_response('admin/usage.html', context={
        'records': logs,
        'brand': settings.INSTANCE_BRAND
    })


@login_required
def single_device(request, device_name):
    try:
        device = MobileCam.objects.filter(groups=request.user.groups.all()).get(name=device_name)
    except MobileCam.DoesNotExist as e:
        return redirect('/usage')
    except Exception as e:
        print(e)

    logs = sessionLog.objects.filter(device=device)

    if request.GET.get('export_last_week', None) is not None:
        logs = logs.filter(begin_timestamp__gt=datetime.datetime.now() - datetime.timedelta(days=7))
        return export_usage_csv(logs)

    paginator = Paginator(logs, 25)

    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        logs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        logs = paginator.page(paginator.num_pages)

    return render_to_response('usage/index.html', context={
        'records': logs,
        'single_device': device,
        'brand': settings.INSTANCE_BRAND
    })
