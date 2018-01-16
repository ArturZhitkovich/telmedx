from django.conf.urls import url

# TODO REMOVE THIS LOGOUT
from users import views as users_views
from . import views

urlpatterns = [
    url(r'^$', views.device_view),
    url(r'^index/(?P<device_name>.*?)/?$', views.index),
    url(r'^index3/(?P<device_name>.*?)/?$', views.index3),
    url(r'^img/(?P<device_name>.*?)/img\d+.jpg$', views.rx_image),
    url(r'^snapshotResponse/(?P<device_name>.*?)/snap\d+.jpg', views.snapshot_response),
    url(r'^stream/(?P<device_name>.*?)/?$', views.get_stream_request),
    url(r'^lastFrame/(?P<device_name>.*?)/(?P<fnum>\d+)$', views.get_last_frame_from_stream),
    url(r'^invite', views.invite_request),
    url(r'^stop', views.stop_request),
    url(r'^snapshot/(?P<device_name>.*?)/?$', views.snapshot_request),
    url(r'^ie-snapshot/(?P<device_name>.*?)/(?P<salt>.*?)$', views.get_ie_snapshot),
    url(r'^flashlight/(?P<device_name>.*?)/?$', views.toggle_flash),
    url(r'^flipcamera/(?P<device_name>.*?)/?$', views.flip_camera),
    url(r'^flashlightResponse/(?P<device_name>.*?)/(?P<status>\w+)/?', views.flashlight_response),
    url(r'^flipcameraResponse/(?P<device_name>.*?)/(?P<status>\w+)/?', views.flipcamera_response),
    url(r'^ping$', views.pingRequest),
    url(r'^ping2/(?P<app_version>\d+\.\d+\.\d+)/(?P<device_name>.*?)/?$', views.ping2_request),
    url(r'^deviceList$', views.device_view),
    url(r'^initializeDevice', views.initialize_device),
    url(r'^imageDownload', views.image_download),
    url(r'^viewSessionInfo', views.view_session_info),
    url(r'^logout$', users_views.logout_view, name='user-logout'),

]
