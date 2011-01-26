#!/bin/env python
from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime                  import *
from nell.tools.TimeAccounting import TimeAccounting
from sesshuns.models           import *
from sets                      import Set

import sys

if len(sys.argv) > 1:
    from nell.utilities.database.DSSDatabase import DSSDatabase
    db = DSSDatabase(database = 'dss_prime')
    db.append(sys.argv[1])
else:
    print "%s requires one argument, the name of the semester to transfer (i.e. 09C, 10A, etc.)" \
          % sys.argv[0]

