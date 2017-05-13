from django.contrib import admin

from ttux.models import mobileCam


class MobileAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(mobileCam, MobileAdmin)
