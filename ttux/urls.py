# ttux application urls

#from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

urlpatterns = patterns('ttux.views',
    url(r'^$', 'deviceView'),
    url(r'^index/(?P<device_name>\w+)$', 'index'),
    url(r'^img\d+.jpg$', 'rxImage'),
    url(r'^snapshotResponse/snap\d+.jpg', 'snapshotResponse'),
    url(r'^stream','getStreamRequest'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot$', 'snapshotRequest'),
    url(r'^ping$', 'pingRequest'),
    url(r'^deviceList$', 'deviceView'),
    #
    url(r'^logout$','logout_view'),
)
