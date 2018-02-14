from http import HTTPStatus

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy

from users import models, views

User = models.TelmedxUser


class MockSession:
    def __setitem__(self, key, value):
        return ''

    def __getitem__(self, item):
        return ''

    def get(self, key=''):
        return ''

    def flush(self):
        return True


class TestUserViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session_middleware = SessionMiddleware()
        self.normal_user = User(
            username='jdoe',
            email='jdoe@example.com',
            password='123123'
        )
        self.superuser = User(
            username='jdoe2',
            email='jdoe3@example.com',
            password='123123',
            is_superuser=True,
            is_staff=True
        )
        self.g_user = User(
            username='jdoe3',
            email='jdoe3@example.com',
            password='123123',
            is_superuser=False,
            is_staff=True
        )

    def test_logout(self):
        request = self.factory.get('logout')
        request.user = self.normal_user
        request.session = MockSession()
        response = views.logout_view(request)
        assert response.status_code == HTTPStatus.FOUND.value

        # Test no user/anonymous user
        request.user = AnonymousUser()
        response = views.logout_view(request)
        assert response.status_code == HTTPStatus.FOUND.value

    def test_login(self):
        # normal_url = reverse_lazy('device-home')
        super_url = reverse_lazy('admin-groups-list')
        g_admin_url = reverse_lazy('admin-users-list')

        user_url_pairs = (
            # (self.normal_user, normal_url),
            (self.superuser, super_url),
            (self.g_user, g_admin_url),
        )

        for user, url in user_url_pairs:
            request = self.factory.get('login')
            request.user = user
            response = views.TelmedxLoginView.as_view()(request)

            assert response.status_code == HTTPStatus.FOUND.value
            assert response.url == url
