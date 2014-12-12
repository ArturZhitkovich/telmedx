# Telmedx device administration

from ttux.models import mobileCam
from django.contrib import admin

#admin.site.register(mobileCam)

class MobileAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(mobileCam, MobileAdmin)