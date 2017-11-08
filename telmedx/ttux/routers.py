from rest_framework import routers
# from .views import InitDeviceViewSet


router = routers.SimpleRouter()
# router.register(r'initialize', InitDeviceViewSet, base_name='api')

urlpatterns = router.get_urls()

