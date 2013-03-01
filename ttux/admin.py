#################################################################################
# @file admin.py
# @brief  Telmedx device administration
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Author          Description
#    July 2012    Tereus Scott    Initial implementation
#################################################################################

from ttux.models import mobileCam
from django.contrib import admin

#admin.site.register(mobileCam)

class MobileAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid')

admin.site.register(mobileCam, MobileAdmin)