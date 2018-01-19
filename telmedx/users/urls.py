from django.conf.urls import url

from users.ajax import *
from users.views import *

urlpatterns = (
    url(r'^users$', TelmedxAdminUsersListView.as_view(), name='admin-users-list'),
    url(r'^users/(?P<pk>\d+)/delete$', TelmedxAdminUsersDeleteView.as_view(), name='admin-users-delete'),
    url(r'^groups$', TelmedxGroupListView.as_view(), name='admin-groups-list'),

    # Non-AJAX
    # url(r'^groups/create/$', TelmedxGroupCreateView.as_view(), name='admin-groups-create'),
    # url(r'^groups/(?P<pk>\d+)/update$', TelmedxGroupsUpdateView.as_view(), name='admin-groups-update'),
    # url(r'^users/create$', TelmedxAdminUsersCreateView.as_view(), name='admin-users-create'),
    # url(r'^users/update/(?P<pk>\d+)$', TelmedxAdminUsersUpdateView.as_view(), name='admin-users-update'),
    # url(r'^users/(?P<pk>\d+)/update$', post_admin_user_form, name='admin-users-update'),

    # AJAX
    url(r'^users/form/(?P<pk>\d+)?$', UserAndProfileFormView.as_view(), name='admin-users-form'),
    url(r'^users/(?P<pk>\d+)/update$', UserAndProfileFormView.as_view(), name='admin-users-update'),
    url(r'^groups/form/(?P<pk>\d+)?$', GroupAndProfileFormView.as_view(), name='admin-groups-form'),
    url(r'^groups/(?P<pk>\d+)/update$', GroupAndProfileFormView.as_view(), name='admin-groups-update'),
)
