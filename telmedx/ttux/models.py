from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class MobileCam(models.Model):
    groups = models.ForeignKey(Group, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.OneToOneField(User, blank=True, null=True, related_name='mobile_cam', on_delete=models.CASCADE)
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
    mobile = models.ForeignKey(MobileCam, on_delete=models.CASCADE)  # the mobile device used for this session
    sessn_date = models.DateTimeField('Session Date')  # the date/time of this session
    streamId = models.CharField(
        max_length=50)  # the session id used for this stream, video and snapshots will be stored here
    userId = models.CharField(max_length=100)  # user id that started this session


class sessionLog(models.Model):
    device = models.ForeignKey(MobileCam, on_delete=models.CASCADE)
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
        seconds = (self.end_timestamp - self.begin_timestamp).total_seconds()
        if seconds < 60:
            ret = '{} seconds'.format(round(seconds, 2))
        else:
            minutes = round((seconds // 60.0), 2)
            plural = 's' if minutes > 1.0 else ''
            ret = '{} minute{}'.format(minutes, plural)

        return ret

    @property
    def begin(self):
        return self.begin_timestamp.strftime('%Y-%m-%d %H:%M:%S')


@receiver(post_save, sender=User)
def create_mobile_cam(sender, instance, created, **kwargs):
    if created:
        MobileCam.objects.create(user=instance)
