from django.apps import AppConfig


class TtuxConfig(AppConfig):
    name = 'ttux'

    def ready(self):
        from .models import MobileCam
        from .session import Session
        deviceList = MobileCam.objects.all().order_by('name')
        for d in deviceList:
            Session.put(d.name)
