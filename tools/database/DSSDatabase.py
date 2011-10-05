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


    def assign_periods_to_windows(self):
        # This function is currently not being called.  It looks like it
        # works fine, but we're looking at ALL Windows & Periods - seems
        # like we just limit this to the new Windows & Periods.
        # Story: https://www.pivotaltracker.com/story/show/14431567
        windows = Window.objects.all()
        for w in windows:
            self.assign_periods_to_window(w)

    def assign_periods_to_window(self, window):
        """
        The cadence table in dss_prime tells us how to set up our window
        time ranges, but it does not tell us how which periods are the 
        default period for each window - it can't, this is an idea that only
        exists in DSS, not in Carl's tools.  So, we have to try and match
        up periods from this session that fall into each window.
        """

        # this funciton isn't being called.  See Story above.

        # nothing to do if this window already has one
        if window.default_period is not None:
            return

        # what periods overlap w/ this window?
        ps = Period.get_periods(window.start_datetime()
                              , window.duration * 24 * 60 # minutes
                              , ignore_deleted = False)

        # debug
        #print " periods in win: ", window.start_datetime(), window.duration
        #print ps
        #print " periods for session: ", window.session.period_set.all()
        
        # which of them belong to this session?
        sps = [p for p in ps if p.session == window.session]

        # the only exceptable result is for there to be just one period now:
        # no periods means the window is still un-initialized, and more
        # then one period means a human has to intervene.
        if len(sps) == 1:
            window.default_period = sps[0]
            window.save()
        elif len(sps) == 0:
            print "NO PERIOD for window: ", window
            pass
        else:
            print "> 1 PERIOD for window: ", window, sps
            pass

    def validate_receiver_schedule(self):
        "Does this rcvr schedule make sense compared to other items?"
        self.check_periods_and_rcvrs()
        self.check_maintenance_and_rcvrs()

    def check_periods_and_rcvrs(self):
        "compares the periods brought over by schedtime w/ the rcvr schedule."

        # make sure we don't have periods scheduled at times where
        # there isn't a required rcvr available
        ps = Period.objects.all()
        bad = []
        for p in ps:
            if not p.has_required_receivers():
                #print "bad period: ", p
                bad.append(p)
        # report
        for b in bad:
            print "Session (%s, %d) at %s for %f hours needs rcvrs: %s" % \
                (b.session.name
               , b.session.original_id
               , b.start
               , b.duration
               , b.session.receiver_list_simple())
        print "number of periods w/ out required receivers: ", len(bad)

    def check_maintenance_and_rcvrs(self):
        "Are there rcvr changes happening w/ out maintenance days?"
        bad = []
        # cast a wide enough net to make this semester agnostic
        start = date(2000, 1, 1)
        days = 365 * 20
        schedule = Receiver_Schedule.extract_schedule(start, days)
        changes = schedule.items()
        # the first date is a date, not a datetime, ignore it.
        for dt, rcvrs in changes[1:]:
            # is there a maintanence day this day?
            # well, what are the periods for this day?
            start_day = dt.replace(hour = 0
                                 , minute = 0
                                 , second = 0
                                 , microsecond = 0)
            end_day = start_day + timedelta(days = 1)
            day_periods = Period.objects.filter(start__gt = start_day
                                              , start__lt = end_day)
            # of these, is any one of them a maintenance?
            maintenance = [p for p in day_periods \
                if p.session.project.is_maintenance()]
            if len(maintenance) == 0:
                bad.append(dt)

        print "Rcvr changes w/ out maintenance day: "
        bad.sort()
        for b in bad:
            print b

