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

from datetime            import datetime, timedelta, date
import time

from test_utils import NellTestCase
from scheduler.models import *
from scheduler.httpadapters import EventJson
from scheduler.tests.utils  import create_sesshun
from scheduler.tests.utils               import create_blackout

class TestEventJson(NellTestCase):

    def setUp(self):
        "Setup various objects we want to feed into EventJson"
        super(TestEventJson, self).setUp()

        self.ej = EventJson()

        # create some user blackouts
        self.u = User(first_name = "Test"
                    , last_name  = "User"
                      )
        self.u.save()

        self.blackout1 = create_blackout(user = self.u,
                                         repeat = "Once",
                                         start = datetime(2009, 1, 1, 11),
                                         end = datetime(2009, 1, 3, 11))

        self.blackout2 = create_blackout(user = self.u,
                                         repeat = 'Weekly',
                                         start  = datetime(2009, 1, 4, 11),
                                         end    = datetime(2009, 1, 4, 13),
                                         until  = datetime(2009, 5, 4, 11))

        # create some project blackouts
        semester = Semester.objects.get(semester = "08C")
        ptype    = Project_Type.objects.get(type = "science")

        self.pcode = 'newProject' 
        self.project = Project(semester = semester
                             , project_type = ptype
                             , pcode = self.pcode
                               )
        self.project.save()

        self.blackout3 = create_blackout(project  = self.project,
                                         timezone = 'UTC',
                                         repeat   = 'Once',
                                         start    = datetime(2008, 10, 1, 11),
                                         end      = datetime(2008, 10, 3, 11))

        # put the user on the project
        inv = Investigator(user = self.u
                         , project = self.project
                         , observer = True
                          )
        inv.save()

        # create a windowed session
        self.s = create_sesshun()
        self.s.project = self.project
        self.s.session_type = Session_Type.objects.get(type = 'windowed')
        self.s.save()

        # create some windows and periods
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.p = Period(session = self.s
                 , start = datetime(2009, 1, 4, 10)
                 , duration = 1.0
                 , accounting = pa
                 , state = Period_State.get_state('S')
                  )
        self.p.save()

        self.w = Window(session = self.s)
        self.w.save()
        self.wr1 = WindowRange(window = self.w
                       , start_date = date(2009, 1, 1)
                       , duration = 6
                         )
        self.wr1.save()
        self.wr2 = WindowRange(window = self.w
                       , start_date = date(2009, 1, 10)
                       , duration = 3
                         )
        self.wr2.save()                 

        self.p.window = self.w
        self.p.save()

    def test_getEvents(self):

        # test all the events retrieved for these two weeks
        start = datetime(2009, 1, 1)
        end   = datetime(2009, 1, 15)

        # what a pain in the ass: need to convert times to floats
        fmt = "%Y-%m-%d %H-%M-%S"
        startStr = start.strftime(fmt)
        endStr = end.strftime(fmt)
        start = time.mktime(time.strptime(startStr, fmt))
        end   = time.mktime(time.strptime(endStr,   fmt))
        result = self.ej.getEvents(self.project, start, end, 'UTC')

        # Now, since we don't have control of reservations, 
        # if there is a reservation, remove it
        filteredResult = [r for r in result if not r.has_key('className')\
            or r['className'] != 'reservation']
        # We have to remove the id as well, since there's no guarantee 
        # what this will be
        for r in filteredResult:
            r.pop('id')
    
        # number of semesters just depends on how many semesters are 
        # in the DB are and are in the future, so separate these out
        rest = []
        semesters = []
        for r in filteredResult:
            if r['className'] == 'semester':
                semesters.append(r)
            else:
                rest.append(r)


        # now we can be sure what the rest should be:
        exp = [{'className': 'blackout'
              , 'start': '2009-01-01T11:00:00+00:00'
              , 'end': '2009-01-03T11:00:00+00:00'
              , 'title': u'Test User: blackout'}
             ,{'className': 'blackout'
             , 'start': '2009-01-04T11:00:00+00:00'
             , 'end': '2009-01-04T13:00:00+00:00'
             , 'title': u'Test User: blackout'}
             , {'className': 'blackout'
             , 'start': '2009-01-11T11:00:00+00:00'
             , 'end': '2009-01-11T13:00:00+00:00'
             , 'title': u'Test User: blackout'}
             ,{'className': 'period'
             , 'start': '2009-01-04T10:00:00+00:00'
             , 'end': '2009-01-04T11:00:00'
             , 'title': u'Observing Low Frequency With No RFI'} 
             ,{'className': 'window'
             , 'start': '2009-01-01T00:00:00'
             , 'end': '2009-01-06T23:45:00'
             , 'title': u'Window Low Frequency With No RFI'}
             , {'className': 'window'
             , 'start': '2009-01-10T00:00:00'
             , 'end': '2009-01-12T23:45:00'
             , 'title': u'Window Low Frequency With No RFI'}
              ]

        self.assertEqual(6, len(rest))
        for e in exp:
            self.assertTrue(e in rest)

    def test_periodJson(self):
        
        json = self.ej.periodJson(self.p, 5, 'UTC')
        exp = {'className': 'period'
             , 'start': '2009-01-04T10:00:00+00:00'
             , 'end': '2009-01-04T11:00:00'
             , 'id': 5
             , 'title': 'Observing Low Frequency With No RFI'} 
        self.assertEqual(exp, json) 

    def test_windowRangeJson(self):
        
        json = self.ej.windowRangeJson(self.wr1, 5)
        exp = {'className': 'window'
             , 'start': '2009-01-01T00:00:00'
             , 'end': '2009-01-06T23:45:00'
             , 'id': 5
             , 'title': 'Window Low Frequency With No RFI'}
        self.assertEqual(exp, json) 

        json = self.ej.windowRangeJson(self.wr2, 6)
        exp = {'className': 'window'
             , 'start': '2009-01-10T00:00:00'
             , 'end': '2009-01-12T23:45:00'
             , 'id': 6
             , 'title': 'Window Low Frequency With No RFI'}
        self.assertEqual(exp, json) 

    def test_blackoutJson(self):

        # user blackout
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        s = time.mktime(calstart.timetuple())
        e = time.mktime(calend.timetuple()) 

        json = self.ej.blackoutJson(self.blackout1, s, e)
        event = {'className': 'blackout'
               , 'start': '2009-01-01T11:00:00'
               , 'end': '2009-01-03T11:00:00'
               , 'id': 1L
               , 'title': 'Test User: blackout'
               }
        self.assertEqual(event, json[0])

        # project blackout
        calstart = datetime(2008, 10, 1)
        calend   = datetime(2008, 10, 30)
        s = time.mktime(calstart.timetuple())
        e = time.mktime(calend.timetuple()) 
        json = self.ej.blackoutJson(self.blackout3, s, e)
        event = {'className': 'blackout'
               , 'start': '2008-10-01T11:00:00'
               , 'end': '2008-10-03T11:00:00'
               , 'id': 3L
               , 'title': '%s: blackout' % self.pcode
               }
        self.assertEqual(event, json[0])


