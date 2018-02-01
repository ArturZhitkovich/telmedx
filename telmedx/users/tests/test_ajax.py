import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory

from users import models, ajax

User = models.TelmedxUser


class TestObjectProfileView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.normal_user = User(
            username='jdoe',
            email='jdoe@example.com',
            password='123123'
        )

    def test_urls_protected(self):
        view_group = ajax.GroupAndProfileFormView.as_view()
        view_user = ajax.UserAndProfileFormView.as_view()

        request = self.factory.get('group/form')
        request.user = AnonymousUser()

        with pytest.raises(PermissionDenied):
            response_group = view_group(request)

        with pytest.raises(PermissionDenied):
            response_user = view_user(request)

    def test_get_action_url_none(self):
        """
        Ensure this raises an exception
        :return:
        """
        view = ajax.ObjectAndProfileFormView
        with pytest.raises(ValueError):
            v = view()
            v.get_action_url()

    def test_get_action_url_populated(self):
        """
        Ensure action url is actually returned
        :return:
        """
        view = ajax.ObjectAndProfileFormView()
        view.action_url = 'Something'
        assert view.get_action_url() == 'Something'
