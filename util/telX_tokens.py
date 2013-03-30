'''
@brief: telX_tokens - general utility to handle & generate and manage tokens
Created on 2013-03-10

@author: developer
'''
from datetime import datetime
from django.conf import settings
from django.utils.hashcompat import sha_constructor
import random

def makeUniqueToken(request):
    '''generate a unique token string that will be used as the long key for phone to server requests after the session is established'''
    
    timestamp = datetime.today()
    myhash = sha_constructor(settings.SECRET_KEY + unicode(request.user.id) + request.user.password + unicode(timestamp)).hexdigest()[::2]
    t =  "%s%s" % (timestamp, myhash)
    t = t.replace(" ", "") # remove spaces
    t = t.replace(":","")
    t = t.replace("-", "")
    t = t.replace(".","")    
    return t

def makeOneTimeUseKey():
    '''generate a random four digit number, return as a string'''
    rnd = random.randint(1000,9999)
    return(str(rnd))