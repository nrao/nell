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

from datetime            import datetime, timedelta

from scheduler.httpadapters                 import *
from scheduler.models                       import *
from test_utils                            import BenchTestCase, timeIt
from utils                                 import *
from utils                   import create_sesshun
from tools.alerts.PeriodChanges import PeriodChanges
from tools.RevisionUtilityTester import RevisionUtilityTester
from tools.RevisionUtilityTester import VersionTester
from utilities.VersionDiff import VersionDiff

class TestPeriodChanges(BenchTestCase):

    def setUp(self):
        super(TestPeriodChanges, self).setUp()

        self.ps = []
        #now = datetime.now()
        #s = Sesshun.objects.all()[0]
        s = create_sesshun()
        pending = Period_State.get_state("P")
        #start = now + timedelta(hours = 1) 
        #start = start.replace(minute = 0, second = 0, microsecond = 0)
        start = datetime(2011, 2, 9, 11)
        self.start = start
        for i in range(1):
        
            duration = 4.0 # hrs
            start = start + timedelta(hours = duration)
    
            pa = Period_Accounting(scheduled = duration)
            pa.save()
        
            p = Period(session = s
                     , start = start
                     , duration = duration
                     , state = pending
                     , accounting = pa
                     , score = 0.0
                     , forecast = datetime.now()
                      )
            p.save()
            self.ps.append(p)

    def test_getChangesForNotification_2(self):

        pc = PeriodChanges(test = True)
        
        # What would the revision system return for these non-changed periods?
        pc.revisions.versions = {self.ps[0] : [VersionTester(fields = {'state' : 1}
                                                           , dt = self.start)]
                               , self.ps[0].accounting : [VersionTester(dt = self.start)]
                                }
          
        pc.revisions.diffs = {self.ps[0] : []
                            , self.ps[0].accounting : []}


        pdiffs = [(p, pc.getChangesForNotification(p)) for p in self.ps]

        self.assertEquals(pdiffs[0][0], self.ps[0])
        self.assertEquals(pdiffs[0][1], [])

        # now move the period to published, and decrease it's duration
        self.ps[0].publish()
        self.ps[0].save()
        self.ps[0].duration = 3
        self.ps[0].save()

        # What would the revision system look like?
        dt1 = self.start + timedelta(minutes = 1)
        dt2 = self.start + timedelta(minutes = 2)
        pc.revisions.versions = {self.ps[0] : [VersionTester(fields = {'state' : 1}
                                                           , dt = self.start)
                                             , VersionTester(fields = {'state' : 2}
                                                           , dt = dt1)
                                             , VersionTester(fields = {'state' : 2}
                                                          , dt = dt2)
                                                           ]

                               , self.ps[0].accounting : [VersionTester(dt = self.start)
                                                        , VersionTester(dt = dt1)
                                                        , VersionTester(dt = dt2)
                                                        ]
                                }
   
        scheduledDiff =                     VersionDiff(dt = dt2
                                                      , field = 'duration'
                                                      , value1 = 4.0
                                                      , value2 = 3.0)
        pc.revisions.diffs = {self.ps[0].accounting : []
                            , self.ps[0] : [VersionDiff(dt = dt1
                                                      , field = 'state'
                                                      , value1 = 1
                                                      , value2 = 2)
                                          , scheduledDiff            
                                            ]
                               }             

                               
        pdiffs = [(p, pc.getChangesForNotification(p)) for p in self.ps]

        self.assertEquals(pdiffs[0][0], self.ps[0])
        self.assertEquals(len(pdiffs[0][1]), 1)
        self.assertEquals(pdiffs[0][1][0], scheduledDiff) 

    def test_getStates(self):
       
        p = self.ps[0]
        pc = PeriodChanges(test = True)
        
        # What would the revision system return for ths non-changed period?
        version = VersionTester(fields = {'state' : 1}, dt = self.start)

        states = pc.getStates([version])                                
        self.assertEquals([(self.start, 1)], states)

        # What would the revision system look like for some changes?
        dt1 = self.start + timedelta(minutes = 1)
        dt2 = self.start + timedelta(minutes = 2)        
        v1 = VersionTester(fields = {'state' : 2}, dt = dt1)
        v2 = VersionTester(fields = {'state' : 2}, dt = dt2)
        states = pc.getStates([version, v1, v2])                               
        exp = [(self.start, 1)
             , (dt1, 2)
             , (dt2, 2)
              ]
        self.assertEquals(exp, states)

    def test_getNewChangeDate(self):

        p = self.ps[0]
        pc = PeriodChanges(test = True)
        
        # What would the revision system return for ths non-changed period?
        version = VersionTester(fields = {'state' : 1}, dt = self.start)

        dt, states = pc.getNewChangeDate(p, [version])                                
        self.assertEquals([(self.start, 1)], states)
        self.assertEquals(None, dt)

        # What would the revision system look like for some changes?
        dt1 = self.start + timedelta(minutes = 1)
        dt2 = self.start + timedelta(minutes = 2)        
        v1 = VersionTester(fields = {'state' : 2}, dt = dt1)
        v2 = VersionTester(fields = {'state' : 2}, dt = dt2)
        dt, states = pc.getNewChangeDate(p, [version, v1, v2])                               
        exp = [(self.start, 1)
             , (dt1, 2)
             , (dt2, 2)
              ]
        self.assertEquals(exp, states)
        self.assertEquals(dt1, dt)

        # now, pretend like a notification was made between the the
        # last two versions
        p.last_notification = dt1 + timedelta(seconds = 30)
        dt, states = pc.getNewChangeDate(p, [version, v1, v2])                               
        self.assertEquals(exp, states)
        self.assertEquals(dt2, dt) # notice how the expected time changes

    def test_getChangesForNotification(self):

        p = self.ps[0]
        pc = PeriodChanges(test = True)
        
        # What would the revision system return for ths non-changed period?
        version = VersionTester(fields = {'state' : 1}, dt = self.start)
        pc.revisions.versions = {p : [version]}

        diffs = pc.getChangesForNotification(p)                                
        self.assertEquals([], diffs)

        # What would the revision system look like for some changes?
        dt1 = self.start + timedelta(minutes = 1)
        dt2 = self.start + timedelta(minutes = 2)        
        v1 = VersionTester(fields = {'state' : 2}, dt = dt1)
        v2 = VersionTester(fields = {'state' : 2}, dt = dt2)
        pc.revisions.versions = {p : [version, v1, v2]}
        schdDiff = VersionDiff(dt = dt1
                             , field = 'state'
                             , value1 = 1
                             , value2 = 2)
        durDiff  = VersionDiff(dt = dt2
                             , field = 'duration'
                             , value1 = 4.0
                             , value2 = 3.0)
        pc.revisions.diffs = {p.accounting : []
                            , p            : [schdDiff, durDiff]
                              }
        
        diffs = pc.getChangesForNotification(p)                                
        self.assertEquals(1, len(diffs))
        self.assertEquals(durDiff, diffs[0])

        # set the last notification to be past these changes,
        # and notice how now there's nothing new to report!
        p.last_notification = dt2 + timedelta(days = 1)
        diffs = pc.getChangesForNotification(p)                            
        self.assertEquals(0, len(diffs))
