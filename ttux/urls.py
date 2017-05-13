# ttux application urls

# from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'ttux.views',
    url(r'^$', 'deviceView'),
    url(r'^index/(?P<device_name>.*?)/?$', 'index'),
    url(r'^index3/(?P<device_name>.*?)/?$', 'index3'),
    url(r'^img/(?P<device_name>.*?)/img\d+.jpg$', 'rxImage'),
    url(r'^snapshotResponse/(?P<device_name>.*?)/snap\d+.jpg', 'snapshotResponse'),
    url(r'^stream/(?P<device_name>.*?)/?$', 'getStreamRequest'),
    url(r'^lastFrame/(?P<device_name>.*?)/(?P<fnum>\d+)$', 'getLastFrameFromStream'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot/(?P<device_name>.*?)/?$', 'snapshotRequest'),
    url(r'^ie-snapshot/(?P<device_name>.*?)/(?P<salt>.*?)$', 'get_ie_snapshot'),
    url(r'^flashlight/(?P<device_name>.*?)/?$', 'toggleFlash'),
    url(r'^flipcamera/(?P<device_name>.*?)/?$', 'flipCamera'),
    url(r'^flashlightResponse/(?P<device_name>.*?)/(?P<status>\w+)/?', 'flashlightResponse'),
    url(r'^flipcameraResponse/(?P<device_name>.*?)/(?P<status>\w+)/?', 'flipcameraResponse'),
    url(r'^ping$', 'pingRequest'),
    url(r'^ping2/(?P<app_version>\d+\.\d+\.\d+)/(?P<device_name>.*?)/?$', 'ping2Request'),
    url(r'^deviceList$', 'deviceView'),
    url(r'^initializeDevice', 'initialize_device'),
    url(r'^viewSessionInfo', 'view_session_info'),
    url(r'^logout$', 'logout_view'),
)
