# ttux application urls
from django.conf.urls import patterns, include, url

urlpatterns = patterns('ttux.views',
    url(r'^img$', 'rxImage'),
    url(r'^snapshotResponse', 'snapshotResponse'),
    url(r'^stream','getStreamRequest'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot', 'snapshotRequest'),

    url(r'^logout$','logout_view'),
)
