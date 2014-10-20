# ttux application urls

#from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

urlpatterns = patterns('usage.views',
    url(r'^$', 'home'),
    url(r'^device/(?P<device_name>\w+)$', 'single_device')
)
