from django.conf import settings
from django.test import TestCase
from django.views.generic import View

from users import mixins


class MockBaseView(mixins.BaseTelmedxMixin, View):
    pass


class MixinsTestCase(TestCase):
    def setUp(self):
        settings.INSTANCE_BRAND = 'brand'

    def test_base_mixin_context_data(self):
        view = MockBaseView()
        data = view.get_context_data()
        assert data.get('brand') == 'brand'
