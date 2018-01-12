"""telmedx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin

from ttux import views as ttux_views
from ttux.routers import urlpatterns as ttux_patterns
from users.views import TelmedxLoginView, TelmedxAdminUsersListView, TelmedxAdminUsersUpdateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', TelmedxLoginView.as_view()),
    url(r'^login/$', TelmedxLoginView.as_view(), name='login'),
    url(r'^tadmin/', include('users.urls')),

    url(r'^ttux/', include('ttux.urls')),
    url(r'^usage/', include('usage.urls')),
    url(r'^login-and-view/(?P<device_name>\w+)/?$', ttux_views.sso_login_view),
    url(r'^devices/?$', ttux_views.device_view),
    url(r'^device/(?P<device_name>.*?)/?$', ttux_views.index3),
    # url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_ROOT}),
    url(r'^api', include(ttux_patterns))
]
