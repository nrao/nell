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

from datetime                     import date, datetime, timedelta
from tools.database.DSSPrime2DSS  import DSSPrime2DSS
from utilities.database.external.AstridDB     import AstridDB
from scheduler.models             import *

import sys

class DSSDatabase(object):

    """
    This class is responsible for populating a DSS database that has already
    been primed with static information (observing types table, etc.) with
    the data necessary for running the DSS for a semester.
    The main tasks are: transferring data from an intermediary DB that
    Carl populates, tranferring raw tables we get from Carl's system.
    To prepare the database for a specific semester (including things like
    rcvr schedules), this class should be extended.
    """

    def __init__(self, database = "dss_prime"
                     , interactive = False
                     , test = False ):

        self.interactive = interactive

        # responsible for data transfers
        self.dss_prime = DSSPrime2DSS(database = database)

        # be careful w/ the turtle DB
        dbname = "turtle" if not test else "turtle_sim"
        self.astridDB = AstridDB(dbname = dbname, test = test)

    def create(self, semester):
        "Method for creating a new DSS database "
        # Transfer the stuff that is semester independent
        self.dss_prime.transfer()
        
        # we no longer create new DSS DB's really, except for testing
        # so won't bother w/ astrid codes here.

    def append(self, semester):
        "Method for appending new semester data to existing DSS database"

        self.dss_prime.transfer_only_new()
        
        # transfer project codes to astrid
        self.astridDB.addProjects(self.dss_prime.new_projects)

