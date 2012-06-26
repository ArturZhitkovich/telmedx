# ttux application urls

#from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

urlpatterns = patterns('ttux.views',
    url(r'^$', 'deviceView'),
    url(r'^index/(?P<device_name>\w+)$', 'index'),
    url(r'^img/(?P<device_name>\w+)/img\d+.jpg$', 'rxImage'),
    url(r'^snapshotResponse/(?P<device_name>\w+)/snap\d+.jpg', 'snapshotResponse'),
    url(r'^stream/(?P<device_name>\w+)$','getStreamRequest'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot/(?P<device_name>\w+)$', 'snapshotRequest'),
    url(r'^ping$', 'pingRequest'),
    url(r'^deviceList$', 'deviceView'),
    #
    url(r'^logout$','logout_view'),
)
