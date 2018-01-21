import pytest
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
