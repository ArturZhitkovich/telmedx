# telmedx data model
from django.db import models
from django.contrib.auth.models import Group
from ttux.utils import HumanTimeFormatter

class mobileCam(models.Model):
    groups         = models.ForeignKey(Group)
    name           = models.CharField(max_length=100)  # name of this device
    uid            = models.CharField(max_length=50)   # unique identifier, for an iphone this will be the phone number, for an iTouch it is??
    streamId       = models.CharField(max_length=50, blank=True)  # stream identifier of the currently connected stream, blank otherwise
    connectedState = models.BooleanField(default=False)      # is the device currently connected
    
class sessionRecord(models.Model):
    mobile     = models.ForeignKey(mobileCam) # the mobile device used for this session
    sessn_date = models.DateTimeField('Session Date') # the date/time of this session
    streamId   = models.CharField(max_length=50) # the session id used for this stream, video and snapshots will be stored here
    userId     = models.CharField(max_length=100) # user id that started this session

class sessionLog(models.Model):
	device = models.ForeignKey(mobileCam)
	begin_timestamp = models.DateTimeField()
	end_timestamp = models.DateTimeField()
	frames = models.IntegerField()

	@property
	def duration(self):
		return self.end_timestamp - self.begin_timestamp
		# return HumanTimeFormatter(self.end_timestamp - self.begin_timestamp).format()

	@property
	def begin(self):
		return self.begin_timestamp.strftime('%Y-%m-%d %H:%M:%S')