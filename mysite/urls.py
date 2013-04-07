#################################################################################
# @file urls.py
# @brief  Telmedx main site url configuraiton
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Author          Description
#    July 2012    Tereus Scott    Initial implementation
#################################################################################
"""Main site url configuration"""

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login
from django.contrib import auth
from django.contrib import admin
from django.conf import settings
import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^ttux/01/', include('ttux.urls')),    # ttux version 01 protocol
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login),
    #url(r'^crossdomain.xml$', views.crossdomainHandler),
    url(r'^$', login),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_ROOT}),
)

# trying to use django cross site support from
# http://docs.b-list.org/django-flashpolicies/1.4.1/policies.html
# need to spend more time because we are not using standard port number!
