from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login
from django.contrib import auth
from django.contrib import admin
#import views

admin.autodiscover()

#import ttux

urlpatterns = patterns('',
    url(r'^ttux/', include('ttux.urls')),
    url(r'^polls/', include('polls.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login),
    url(r'^crossdomain.xml$',
    'flashpolicies.views.simple',
    {'domains': ['*'], 'ports':['*']}),
                       
    #url(r'^crossdomain.xml$', views.crossdomainHandler),
    url(r'^$', login),
)

# trying to use django cross site support from
# http://docs.b-list.org/django-flashpolicies/1.4.1/policies.html
# need to spend more time because we are not using standard port number!