from django.conf.urls import patterns, include, url

from django.contrib.auth.views import login
from django.contrib import auth

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^ttux/', include('ttux.urls')),
    url(r'^polls/', include('polls.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login),
    url(r'^$', login),
)