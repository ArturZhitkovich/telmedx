from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login

admin.autodiscover()

# import ttux

urlpatterns = patterns('',
                       url(r'^ttux/', include('ttux.urls')),
                       url(r'^usage/', include('usage.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^login/$', login),
                       url(r'^login-and-view/(?P<device_name>\w+)/?$', 'ttux.views.sso_login_view'),
                       url(r'^devices/?$', 'ttux.views.deviceView'),  # Alternate for /deviceList
                       url(r'^device/(?P<device_name>.*?)/?$', 'ttux.views.index3'),  # Alternate for /ttux/index3
                       url(r'^$', login),
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATICFILES_ROOT}),
                       )
