#################################################################################
# @file __init__.py
# @brief  ttux site initialization
# @author Tereus Scott
# Creation Date  Sept 28, 2011
# Copyright 2013 telmedx
#  
# Major Revision History
#    Date         Author          Description
#    July 2012    Tereus Scott    Initial implementation
#################################################################################

from ttux.models import mobileCam # get our database model
from ttux.session import Session

#import logging
#logger = logging.getLogger("ttux init:");
#logging.basicConfig(level=logging.DEBUG)

print("ttux init: enter")
#logger.info("Enter")
try:
    deviceList = mobileCam.objects.all().order_by('name')[:4]
    for d in deviceList:
        print "Creating session for device:" + d.name
        Session.put(d.name, Session())
except:
    print("initialization failure, creating db?")

#logger.info("Exit")
print("ttux init: exit")
#Session.put(0, Session())
