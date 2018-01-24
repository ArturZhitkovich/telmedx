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

from ttux import views as ttux_views
from users.jwt_views import obtain_jwt_token
from users.views import TelmedxLoginView
from .api_routers import urlpatterns as api_patterns

urlpatterns = [
    url(r'^$', TelmedxLoginView.as_view()),
    url(r'^login/$', TelmedxLoginView.as_view(), name='login'),
    url(r'^admin/', include('users.urls')),

    url(r'^ttux/', include('ttux.urls')),
    url(r'^usage/', include('usage.urls')),
    url(r'^devices/?$', ttux_views.device_list, name='device-home'),
    url(r'^device/(?P<user_uuid>.*?)/?$', ttux_views.device_detail, name='device-detail'),

    url(r'^api/', include(api_patterns)),
    url(r'^login-and-view/(?P<device_name>\w+)/?$', ttux_views.sso_login_view),
    url(r'^api-token-auth/', obtain_jwt_token),
]
