# Create your views here.
import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render_to_response

from ttux.models import mobileCam, sessionLog
from usage.utils import export_usage_csv


@login_required(login_url='/login')
def home(request):
    logs = sessionLog.objects.filter(device__groups=request.user.groups.all())
    paginator = Paginator(logs, 25)  # Show 25 contacts per page

    page = request.GET.get('page')

    if request.GET.get('export_last_week', None) is not None:
        try:
            device = mobileCam.objects.filter(groups=request.user.groups.all).get(name=request.GET.get('device'))
            logs.filter(device=device)
        except mobileCam.DoesNotExist:
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

    return render_to_response('usage/index.html', {'records': logs})


@login_required(login_url='/login')
def single_device(request, device_name):
    try:
        device = mobileCam.objects.filter(groups=request.user.groups.all).get(name=device_name)
    except mobileCam.DoesNotExist as e:
        return redirect('/usage')

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

    return render_to_response('usage/index.html',
                              {'records': logs, 'single_device': device})
