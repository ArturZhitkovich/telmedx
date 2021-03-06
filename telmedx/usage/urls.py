from django.conf.urls import url

from . import views

urlpatterns = [
    # 'usage.views',
    url(r'^$', views.home),
    url(r'^device/(?P<device_name>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})$', views.single_device),
    url(r'^group/(?P<pk>\d+)$', views.UsageGroupView.as_view(), name='usage-group'),
    url(r'^export/(?P<pk>\d+)$', views.export_logs, name='usage-export'),
]
