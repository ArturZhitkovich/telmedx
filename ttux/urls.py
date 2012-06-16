# ttux application urls
from django.conf.urls import patterns, include, url

urlpatterns = patterns('ttux.views',
    url(r'^$', 'index'),
    url(r'^img\d+.jpg$', 'rxImage'),
    url(r'^snapshotResponse/snap\d+.jpg', 'snapshotResponse'),
    url(r'^stream','getStreamRequest'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot$', 'snapshotRequest'),

    url(r'^logout$','logout_view'),
)
