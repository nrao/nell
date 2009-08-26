import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'nell.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
sys.path.append('/home/dss.gb.nrao.edu/active/python/lib/python2.5/site-packages') 

sys.path.append('/home/sandboxes/mmccarty/dss/')
sys.path.append('/home/sandboxes/mmccarty/dss/nell')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
