import os
import sys
import site
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

 
path='/var/www/telx/mysite'
 

if path not in sys.path:
	sys.path.append(path)

site.addsitedir('/var/www/telx/prodenv/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/var/www/telx')
sys.path.append('/var/www/telx/mysite')
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

activate_env=os.path.expanduser("/var/www/telx/prodenv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))
 
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
