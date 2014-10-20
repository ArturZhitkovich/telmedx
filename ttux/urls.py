# ttux application urls

#from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

urlpatterns = patterns('ttux.views',
    url(r'^$', 'deviceView'),
    url(r'^index/(?P<device_name>\w+)$', 'index'),
    url(r'^index3/(?P<device_name>\w+)$', 'index3'),
    url(r'^img/(?P<device_name>\w+)/img\d+.jpg$', 'rxImage'),
    url(r'^snapshotResponse/(?P<device_name>\w+)/snap\d+.jpg', 'snapshotResponse'),
    url(r'^stream/(?P<device_name>\w+)$','getStreamRequest'),
    url(r'^lastFrame/(?P<device_name>\w+)/(?P<fnum>\d+)$','getLastFrameFromStream'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot/(?P<device_name>\w+)$', 'snapshotRequest'),
    url(r'^flashlight/(?P<device_name>\w+)/?$', 'toggleFlash'),
    url(r'^flipcamera/(?P<device_name>\w+)/?$', 'flipCamera'),
    url(r'^flashlightResponse/(?P<device_name>\w+)/(?P<status>\w+)/?', 'flashlightResponse'),
    url(r'^flipcameraResponse/(?P<device_name>\w+)/(?P<status>\w+)/?', 'flipcameraResponse'),
    url(r'^ping$', 'pingRequest'),
    url(r'^ping2/(?P<app_version>\d+\.\d+\.\d+)/(?P<device_name>\w+)/?$', 'ping2Request'),
    url(r'^deviceList$', 'deviceView'),
    #
    url(r'^viewSessionInfo', 'view_session_info'),
    url(r'^logout$','logout_view'),
)
