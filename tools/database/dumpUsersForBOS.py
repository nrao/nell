#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)
import sys

# supress the stderr coming from the following import
saveout = sys.stderr
# We need to save to this path due to permission's:
# but that means we have to run this as user 'dss'
fsock = open('/users/dss/out.log', 'w')
sys.stderr = fsock

from scheduler.models import *

sys.stderr = saveout

# now we should be printing normally

users = User.objects.all()

for u in users:
    if u.pst_id is not None and u.username() is not None:
        print "%d,%s" % (u.pst_id, u.username())


