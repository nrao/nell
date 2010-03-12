#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *

users = User.objects.all()

for u in users:
    if u.pst_id is not None and u.username is not None:
        print "%d,%s" % (u.pst_id, u.username)


