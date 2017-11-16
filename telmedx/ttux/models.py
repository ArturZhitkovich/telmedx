from django.contrib.auth.models import Group
from django.db import models


# TODO: Is group really required for this?
class mobileCam(models.Model):
    groups = models.ForeignKey(Group)
    name = models.CharField(max_length=100)  # name of this device
    connectedState = models.BooleanField(default=False)  # is the device currently connected
    email = models.EmailField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    first_name = models.CharField(max_length=255, default='')
    phone_number = models.CharField(max_length=32, default='')

    def __str__(self):
        return self.name

    @property
    def name_display(self):
        return self.name.split('@')[0]


class sessionRecord(models.Model):
    mobile = models.ForeignKey(mobileCam)  # the mobile device used for this session
    sessn_date = models.DateTimeField('Session Date')  # the date/time of this session
    streamId = models.CharField(
        max_length=50)  # the session id used for this stream, video and snapshots will be stored here
    userId = models.CharField(max_length=100)  # user id that started this session


class sessionLog(models.Model):
    device = models.ForeignKey(mobileCam)
    begin_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    frames = models.IntegerField()
    captured_images = models.IntegerField()

    def __str__(self):
        return 'Log for {device} on {date}'.format(
            device=self.device,
            date=self.begin_timestamp
        )

    @property
    def duration(self):
        return self.end_timestamp - self.begin_timestamp

    @property
    def begin(self):
        return self.begin_timestamp.strftime('%Y-%m-%d %H:%M:%S')

