from datetime import datetime, timedelta
from time     import mktime

from test_utils              import NellTestCase
from scheduler.models         import *

class TestBlackout(NellTestCase):

    def setUp(self):
        super(TestBlackout, self).setUp()

        # create some user blackouts
        self.u = User(first_name = "Test"
                    , last_name  = "User"
                    , role       = Role.objects.all()[0]
                      )
        self.u.save()

        once = Repeat.objects.get(repeat = 'Once')
        self.blackout1 = Blackout(user       = self.u
                            , repeat     = once
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        self.blackout1.save()

        weekly = Repeat.objects.get(repeat = 'Weekly')
        self.blackout2 = Blackout(user       = self.u
                            , repeat     = weekly
                            , start_date = datetime(2009, 1, 4, 11)
                            , end_date   = datetime(2009, 1, 4, 13)
                            , until      = datetime(2009, 5, 4, 11))
        self.blackout2.save()

        # create some project blackouts
        semester = Semester.objects.get(semester = "08C")
        ptype    = Project_Type.objects.get(type = "science")

        self.pcode = "GBT08C-01"
        self.project = Project(semester = semester
                             , project_type = ptype
                             , pcode = self.pcode
                               )
        self.project.save()

        self.blackout3 = Blackout(project    = self.project
                                , repeat     = once
                                , start_date = datetime(2008, 10, 1, 11)
                                , end_date   = datetime(2008, 10, 3, 11))
        self.blackout3.save()

    def test_eventjson(self):

        # user blackout
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        json = self.blackout1.eventjson(mktime(calstart.timetuple())
                                      , mktime(calend.timetuple()))
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
        json = self.blackout3.eventjson(mktime(calstart.timetuple())
                                      , mktime(calend.timetuple()))
        event = {'className': 'blackout'
               , 'start': '2008-10-01T11:00:00'
               , 'end': '2008-10-03T11:00:00'
               , 'id': 3L
               , 'title': '%s: blackout' % self.pcode
               }
        self.assertEqual(event, json[0])

    def test_isActive(self):
        results = [(b.isActive(b.start_date + timedelta(hours = 2))
                  , b.isActive(b.end_date + timedelta(hours = 2)))
                   for b in Blackout.objects.all()]
        self.assertEqual(results, [(True, False), (True, True), (True, False)])

    def test_generateDates(self):

        # no repeats are easy ...
        dts = [(self.blackout1.start_date, self.blackout1.end_date)]
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        gdts = self.blackout1.generateDates(calstart, calend)
        self.assertEquals(dts, gdts)

        # should be none in June.
        calstart = datetime(2009, 6, 1)
        calend   = datetime(2009, 6, 30)
        gdts = self.blackout1.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

        # repeats are more complicated
        # how does January look?
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        start = self.blackout2.start_date
        end = self.blackout2.end_date
        dts = [(start, end)]
        for i in [1,2,3]:
            dts.append((start + timedelta(days = 7 * i)
                      , end   + timedelta(days = 7 * i)))
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(dts, gdts)

        # outside of calendar start/end, but weekly until May
        calstart = datetime(2009, 2, 1)
        calend   = datetime(2009, 2, 28)
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(4, len(gdts))

        # should be none in June.
        calstart = datetime(2009, 6, 1)
        calend   = datetime(2009, 6, 30)
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

        # should be none in previous June.
        calstart = datetime(2008, 6, 1)
        calend   = datetime(2008, 6, 30)
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

        # no repeats are easy ... even for project blackouts
        dts = [(self.blackout3.start_date, self.blackout3.end_date)]
        calstart = datetime(2008, 10, 1)
        calend   = datetime(2008, 10, 30)
        gdts = self.blackout3.generateDates(calstart, calend)
        self.assertEquals(dts, gdts)

        # test filter outside of blackouts
        calstart = datetime(2011, 10, 1)
        calend   = datetime(211, 10, 30)
        gdts = self.blackout1.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))
        gdts = self.blackout3.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

    def test_projectBlackout(self):
        "Repeat some of the other tests, but for project blackouts"

        self.assertEquals(self.blackout3.forName(), self.project.pcode)
        self.assertEquals(self.blackout3.forUrlId(), self.project.pcode)

