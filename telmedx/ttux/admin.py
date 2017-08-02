from django.contrib import admin
from .models import mobileCam, sessionLog, sessionRecord


admin.register(mobileCam, sessionRecord, sessionLog)
