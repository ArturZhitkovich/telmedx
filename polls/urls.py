from django.conf.urls import patterns, include, url
#from django.contrib.auth.views import login
#from django.contrib import auth

urlpatterns = patterns('polls.views',
    url(r'^img$', 'rxImage'),
    url(r'^snapshotResponse', 'snapshotResponse'),
    url(r'^stream','getStreamRequest'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot', 'snapshotRequest'),
#    url(r'^$', 'index'),
#    url(r'^(?P<poll_id>\d+)/$', 'detail'),
#    url(r'^(?P<poll_id>\d+)/results/$', 'results'),
#    url(r'^(?P<poll_id>\d+)/vote/$', 'vote'),
    url(r'^logout$','logout_view'),
    #url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    #url(r'^accounts/login/$', 'django.contrib.auth.login'),
    #url(r'^accounts/login/$', login),
)

#urlpatterns += patterns('django.contrib.auth.views',
#    url(r'^accounts/login/$', 'login'),                     
#  #url(r'^user/(?P<user_id>\d+)/user_edit/password/$', 'password_change')
#)
