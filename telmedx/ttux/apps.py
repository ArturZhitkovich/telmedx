from django.apps import AppConfig


class TtuxConfig(AppConfig):
    name = 'ttux'

    def ready(self):
        from .models import mobileCam
        from .session import Session
        deviceList = mobileCam.objects.all().order_by('name')
        for d in deviceList:
            Session.put(d.name)