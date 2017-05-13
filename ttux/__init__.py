from ttux.models import mobileCam # get our database model
from ttux.session import Session


# Put all devices into session?
deviceList = mobileCam.objects.all().order_by('name')
for d in deviceList:
    Session.put(d.name, Session())
