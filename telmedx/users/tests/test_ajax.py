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

    def test_urls_anonymous(self):
        view_group = ajax.ajax_group_form
        view_user = ajax.ajax_user_form

        request = self.factory.get('group/form')
        request.user = AnonymousUser()

        response_group = view_group(request)
        response_user = view_user(request)

        assert response_group.status_code == 302
        assert response_user.status_code == 302

    def test_urls_staff(self):
        view_group = ajax.ajax_group_form
        view_user = ajax.ajax_user_form

        request = self.factory.get('group/form')
        self.normal_user.is_staff = True
        self.normal_user.is_superuser = False
        request.user = self.normal_user

        response_group = view_group(request)
        response_user = view_user(request)

        # Able to see user forms, but not group forms
        assert response_group.status_code == 302
        assert response_user.status_code == 200

    def test_urls_superuser(self):
        view_group = ajax.ajax_group_form
        view_user = ajax.ajax_user_form

        request = self.factory.get('group/form')
        self.normal_user.is_staff = True
        self.normal_user.is_superuser = True
        request.user = self.normal_user

        response_group = view_group(request)
        response_user = view_user(request)

        # Able to see user forms, but not group forms
        assert response_group.status_code == 200
        assert response_user.status_code == 200

