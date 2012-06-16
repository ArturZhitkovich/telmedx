#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.core.handlers.wsgi import WSGIHandler as DjangoWSGIApp
from django.core.management import setup_environ

from django.conf import settings
setup_environ(settings)

application = DjangoWSGIApp()
server = WSGIServer(("127.0.0.1", 1234), application)
print "Starting server on http://127.0.0.1:1234"
server.serve_forever()

#from gevent import monkey; monkey.patch_all()
#from gevent.wsgi import WSGIServer
#
#from django.core.handlers.wsgi import WSGIHandler as DjangoWSGIApp
#from django.core.management import setup_environ
#
#from django.conf import settings
#setup_environ(settings)
#
#application = DjangoWSGIApp()
#server = WSGIServer(("127.0.0.1", 1234), application)
#print "Starting server on http://127.0.0.1:1234"
#server.serve_forever()
