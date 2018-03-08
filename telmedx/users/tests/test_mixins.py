import pytest
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.views.generic import View

from users import mixins, models

User = models.TelmedxUser


class MockBaseView(mixins.BaseTelmedxMixin, View):
    pass


class MockProtectedView(mixins.ProtectedTelmedxMixin, View):
    pass


class MixinsTestCase(TestCase):
    def setUp(self):
        settings.INSTANCE_BRAND = 'brand'
        self.factory = RequestFactory()
        self.normal_user = User(
            username='jdoe',
            email='jdoe@example.com',
            password='123123'
        )

    def test_base_mixin_context_data(self):
        """
        Ensure this mixin returns the brand from settings
        :return:
        """
        view = MockBaseView()
        data = view.get_context_data()
        assert data.get('brand') == 'brand'

    def test_normal_user_protected_mixin(self):
        """
        Ensure this mixin does not allow normal users and raises an exception
        :return:
        """
        view = MockProtectedView
        request = self.factory.get('/protected')
        request.user = self.normal_user

        with pytest.raises(PermissionDenied):
            view.as_view()(request)
