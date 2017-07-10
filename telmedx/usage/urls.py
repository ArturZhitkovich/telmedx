from django.conf.urls import url

from . import views

urlpatterns = [
    #'usage.views',
    url(r'^$', views.home),
    url(r'^device/(?P<device_name>\w+)$', views.single_device)
]
