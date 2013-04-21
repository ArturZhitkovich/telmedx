#################################################################################
# @file urls.py
# @brief  url and handler linkage
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Author          Description
#    July 2012    Tereus Scott    Initial implementation
#################################################################################

#from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

urlpatterns = patterns('ttux.views',
    url(r'^$', 'deviceView'),
    #url(r'^index/(?P<device_name>\w+)$', 'index'),
    #url(r'^viewmaster/(?P<device_name>\w+)$', 'viewmaster'),
    url(r'^viewmaster_ticket', 'viewmaster_ticket'),
    #url(r'^img/(?P<device_name>\w+)/img\d+.jpg$', 'rxImage'),
    url(r'^frame$', 'rxImage'),
    #url(r'^snapshotResponse/(?P<device_name>\w+)/snap\d+.jpg', 'snapshotResponse'),
    url(r'^snapshotResponse$', 'snapshotResponse'),
    #url(r'^stream/(?P<device_name>\w+)$','getStreamRequest'),
    url(r'^getDevState/(?P<device_name>\w+)$','getDeviceState'),
    url(r'^lastFrame/(?P<device_name>\w+)/(?P<fnum>\d+)$','getLastFrameFromStream'),
    url(r'^invite', 'inviteRequest'),
    url(r'^stop', 'stopRequest'),
    url(r'^snapshot/(?P<device_name>\w+)$', 'snapshotRequest'),
    url(r'^uiLightOn/(?P<device_name>\w+)$', 'uiLightOnRequest'),
    url(r'^uiLightOff/(?P<device_name>\w+)$', 'uiLightOffRequest'),
    #url(r'^ping/(?P<device_name>\w+)$', 'pingRequest'),
    url(r'^ping$', 'pingRequest'),
    url(r'^deviceList$', 'deviceView'),
    #url(r'^register(?P<key>\w+)$', 'registerKey'),
    url(r'^register$', 'registerKey'),
    url(r'^makeNewSession', 'makeNewSession'),
    #
    url(r'^logout$','logout_view'),
)
