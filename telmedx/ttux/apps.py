from django.apps import AppConfig

from .session import Session

class TtuxConfig(AppConfig):
    name = 'ttux'

    def ready(self):
        from .models import MobileCam
        deviceList = MobileCam.objects.all().order_by('name')
        for d in deviceList:
            Session.put(d.name, Session())
