import os
#import sys

#os.environ['DJANGO_SETTINGS_MODULE'] = 'nell.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
#sys.path.append('/home/dss2.gb.nrao.edu/active/python/lib/python2.6/site-packages') 

#sys.path.append('/home/dss2.gb.nrao.edu/active')
#sys.path.append('/home/dss2.gb.nrao.edu/active/nell')

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()


import sys

sys.path.insert(0, '/home/dss2.gb.nrao.edu/active')
sys.path.insert(0, '/home/dss2.gb.nrao.edu/active/nell')

import settings

import django.core.management
django.core.management.setup_environ(settings)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
