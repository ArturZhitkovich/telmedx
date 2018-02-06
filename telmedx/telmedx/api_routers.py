# from rest_framework import routers
from django.conf.urls import url

# from .views import InitDeviceViewSet
from ttux.api import *
from users.api import *

# router = routers.SimpleRouter()
# router.register(r'initialize', InitDeviceViewSet, base_name='api')
# router.register(r'ping', PingAPIView, base_name='ping')
# router.register(r'ping2', ping_view, base_name='ping2')


urlpatterns = [
    url(r'^ping/(?P<app_version>\d+\.\d+\.\d+)', PingAPIView.as_view()),
    url(r'^snapshot/snap\d+.jpg', SnapshotAPIView.as_view()),
    url(r'^flipCamera/(?P<status>\w+)', FlipCameraAPIView.as_view()),
    url(r'^flashlight/(?P<status>\w+)', FlashlightAPIView.as_view()),

    url(r'^user/(?P<pk>\d+)', UserUpdateAPIView.as_view()),
    url(r'^profile', UserProfileAPIView.as_view()),
]
