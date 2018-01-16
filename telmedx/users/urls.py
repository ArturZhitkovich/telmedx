from django.conf.urls import url

from users.views import *

urlpatterns = (
    url(r'^users$', TelmedxAdminUsersListView.as_view(), name='admin-users-list'),
    url(r'^users/create$', TelmedxAdminUsersCreateView.as_view(), name='admin-users-create'),
    url(r'^users/update/(?P<pk>\d+)$', TelmedxAdminUsersUpdateView.as_view(), name='admin-users-update'),

    url(r'^groups$', TelmedxGroupListView.as_view(), name='admin-groups-list'),
    url(r'^groups/create/$', TelmedxGroupCreateView.as_view(), name='admin-groups-create'),
    url(r'^groups/update/(?P<pk>\d+)$', TelmedxGroupsUpdateView.as_view(), name='admin-groups-update'),

    # AJAX
    url(r'^getForm$', get_admin_form, name='admin-get-form')
)
