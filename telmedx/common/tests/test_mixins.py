import mock
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from rest_framework.response import Response

from users import models
from .. import mixins

User = models.TelmedxUser


class MockView(mixins.TelmedxAPIView):
    def get(self, request):
        device_name = self.get_device_name(request)
        return Response({'device': device_name})


class TestObjectProfileView(TestCase):
    view = MockView

    def setUp(self):
        self.factory = RequestFactory()
        self.normal_user = User.objects.create(
            username='jdoe',
            email='jdoe@example.com',
            password='123123'
        )

    def test_mixin_noauth(self):
        request = self.factory.get('test')
        request.user = AnonymousUser()
        response = self.view.as_view()(request)
        assert isinstance(request.user, AnonymousUser)
        assert response.status_code == 401

    # NOTE: authenticate() must be patched or else the request user will be overwritten
    # as AnonymousUser due to it not really authenticating.
    @mock.patch('rest_framework_jwt.authentication.JSONWebTokenAuthentication.authenticate')
    @mock.patch('rest_framework.permissions.IsAuthenticated.has_permission')
    def test_mixin_auth(self, is_auth, jwt_auth):
        is_auth.return_value = True
        jwt_auth.return_value = (self.normal_user, "TOKEN")
        request = self.factory.get('test')
        request.user = self.normal_user
        response = self.view.as_view()(request)

        assert request.user == self.normal_user
        assert response.status_code == 200

    # NOTE: authenticate() must be patched or else the request user will be overwritten
    # as AnonymousUser due to it not really authenticating.
    @mock.patch('rest_framework_jwt.authentication.JSONWebTokenAuthentication.authenticate')
    @mock.patch('rest_framework.permissions.IsAuthenticated.has_permission')
    def test_mixin_device_name(self, is_auth, jwt_auth):
        is_auth.return_value = True
        jwt_auth.return_value = (self.normal_user, "TOKEN")

        request = self.factory.get('/test')
        request.user = self.normal_user
        response = self.view.as_view()(request)
        assert request.user == self.normal_user
        assert response.status_code == 200
        assert response.data.get('device') == self.normal_user
