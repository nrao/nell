# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

#!/bin/env python
from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime                  import *
from nell.utilities.TimeAccounting import TimeAccounting
from scheduler.models           import *
from sets                      import Set

import sys

if len(sys.argv) > 1:
    from nell.tools.database.DSSDatabase import DSSDatabase
    db = DSSDatabase(database = 'dss_prime')
    db.append(sys.argv[1])
else:
    print "%s requires one argument, the name of the semester to transfer (i.e. 09C, 10A, etc.)" \
          % sys.argv[0]

