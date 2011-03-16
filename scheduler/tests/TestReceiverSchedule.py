from datetime            import datetime, timedelta
from django.test.client  import Client

from scheduler.httpadapters   import *
from scheduler.models         import *
from test_utils              import BenchTestCase, timeIt

class TestReceiverSchedule(BenchTestCase):

    def setUp(self):
        super(TestReceiverSchedule, self).setUp()
        self.client = Client()

        d = datetime(2009, 4, 1, 0)
        for i in range(9):
            start_date = d + timedelta(5*i)
            for j in range(1,4):
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = i + j)
                rs.save()

    def test_toggle_rcvr(self):

        startDt = datetime(2009, 4, 1)
        original_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        dt1 = datetime(2009, 5, 11)
        dt1_rcvrs = original_schd[dt1]

        # take a rcvr out
        result = Receiver_Schedule.toggle_rcvr(dt1, dt1_rcvrs[0]) 
        self.assertEquals(result, (True, None))

        # make sure the schedule looks right
        new_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        for dt in sorted(original_schd.keys()):
            if dt != dt1:
                self.assertEquals(original_schd[dt], new_schd[dt])
            else:
                self.assertEquals(dt1_rcvrs[1:], new_schd[dt])
            
        # put it back in 
        result = Receiver_Schedule.toggle_rcvr(dt1, dt1_rcvrs[0])
        self.assertEquals(result, (True, None))

        # make sure the schedule looks right
        new_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        for dt in sorted(original_schd.keys()):
            self.assertEquals(original_schd[dt], new_schd[dt])

        # change a range of rcvr dates
        start = datetime(2009, 4, 16)
        end = datetime(2009, 5, 1)
        start_rcvrs = original_schd[start]
        tgrcvr = start_rcvrs[0]
        result = Receiver_Schedule.toggle_rcvr(start, tgrcvr, endDt=end)
        self.assertEquals(result, (True, None))

        # make sure the schedule looks right
        new_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        for dt in sorted(original_schd.keys()):
            if dt >= start and dt <= end:
                if tgrcvr in original_schd[dt]:
                    self.assertTrue(tgrcvr not in new_schd[dt])
                else:    
                    self.assertTrue(tgrcvr in new_schd[dt])
            else:
                self.assertEquals(original_schd[dt], new_schd[dt])
            
        # put it back in again
        result = Receiver_Schedule.toggle_rcvr(start, tgrcvr, endDt=end)
        self.assertEquals(result, (True, None))
        new_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        for dt in sorted(original_schd.keys()):
            self.assertEquals(original_schd[dt], new_schd[dt])


    def print_schd(self, schd):
        "Utility for visualizing the receiver schedule"
        for dt in sorted(schd.keys()):
            print dt, [r.abbreviation for r in schd[dt]]

    def test_add_date(self):
        
        startDt = datetime(2009, 4, 1)
        original_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        new_date_rcvrs = original_schd[datetime(2009, 4, 26)]

        # check error checking
        result =  Receiver_Schedule.add_date(datetime(2000, 1, 1))
        self.assertEquals(result[0], False)
        result =  Receiver_Schedule.add_date(datetime(2009, 4, 1))
        self.assertEquals(result[0], False)

        # new added date should be identical to previous one
        newDt = datetime(2009, 4, 28)
        result = Receiver_Schedule.add_date(newDt)
        self.assertEquals((True, None), result)

        new_schd = Receiver_Schedule.extract_schedule(startdate = startDt)
        self.assertEquals(new_date_rcvrs, new_schd[newDt])

    @timeIt
    def test_extract_diff_schedule(self):
        startdate = datetime(2009, 4, 6, 12)
        duration = 15
        diff = Receiver_Schedule.extract_diff_schedule(startdate = startdate,
                                                       days = duration)
        expected = [datetime(2009, 4, 6, 0, 0)
                  , datetime(2009, 4, 11, 0, 0)
                  , datetime(2009, 4, 16, 0, 0)
                  , datetime(2009, 4, 21, 0, 0)]
        self.assertEqual(expected, [d[0] for d in diff])
        jdiff = Receiver_Schedule.jsondict_diff(diff)
        expected = {'diff_schedule': \
            [{'down': [], 'up': [u'RRI', u'342', u'450'], 'day': '04/06/2009'}
           , {'down': [u'RRI'], 'up': [u'600'], 'day': '04/11/2009'}
           , {'down': [u'342'], 'up': [u'800'], 'day': '04/16/2009'}
           , {'down': [u'450'], 'up': [u'1070'], 'day': '04/21/2009'}]}
        self.assertEqual(expected, jdiff)

    def test_extract_schedule1(self):
        startdate = datetime(2009, 4, 6, 12)
        duration = 15
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate,
                                                      days = duration)
        expected = [datetime(2009, 4, 11, 0, 0)
                  , datetime(2009, 4, 16, 0, 0)
                  , datetime(2009, 4, 6, 0, 0)
                  , datetime(2009, 4, 21, 0, 0)]
        self.assertEqual(expected, schedule.keys())
        jschedule = Receiver_Schedule.jsondict(schedule)
        expected = {'04/11/2009': [u'342', u'450', u'600']
                  , '04/16/2009': [u'450', u'600', u'800']
                  , '04/06/2009': [u'RRI', u'342', u'450']
                  , '04/21/2009': [u'600', u'800', u'1070']}
        self.assertEqual(expected, jschedule)

    def test_extract_schedule2(self):
        """
        Making sure we starting counting duration from the startdate
        rather than some previous receiver change date.
        """

        startdate = datetime(2009, 4, 7, 12)
        duration = 14
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate,
                                                      days = duration)
        expected = [datetime(2009, 4, 11, 0, 0)
                  , datetime(2009, 4, 16, 0, 0)
                  , datetime(2009, 4, 6, 0, 0)
                  , datetime(2009, 4, 21, 0, 0)]
        self.assertEqual(expected, schedule.keys())
        jschedule = Receiver_Schedule.jsondict(schedule)
        expected = {'04/11/2009': [u'342', u'450', u'600']
                  , '04/16/2009': [u'450', u'600', u'800']
                  , '04/06/2009': [u'RRI', u'342', u'450']
                  , '04/21/2009': [u'600', u'800', u'1070']}
        self.assertEqual(expected, jschedule)

    def test_previousDate(self):
        self.assertEqual(datetime(2009, 4, 6, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 4, 6, 12)))
        self.assertEqual(datetime(2009, 4, 1, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 4, 5, 23)))
        self.assertEqual(datetime(2009, 5, 11, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 7, 1, 0)))
        self.assertEqual(None,
                         Receiver_Schedule.previousDate(
                             datetime(2009, 4, 1, 0)))

    def test_delete_date(self):
        # get the current schedule
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())

        # delete a date
        Receiver_Schedule.delete_date(dates[-3])

        # get the new schedule
        new_schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates = sorted(new_schedule.keys())

        # should be missing this deleted date
        self.assertEquals(len(new_dates) + 1, len(dates))
        self.assertEquals(False, new_schedule.has_key(dates[-3]))
        # but schedule should'nt have changed except for this date
        for dt in dates:
            if dt != dates[-3]:
                self.assertEquals(new_schedule[dt], schedule[dt])

    @timeIt
    def test_shift_date(self):
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())

        from_date = dates[-3]
        to_date   = from_date + timedelta(days = 1)
        success, msg = Receiver_Schedule.shift_date(from_date, to_date)
        self.assertEquals(True, success)

        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates = sorted(schedule.keys())
        for i in range(len(dates)-3):
            self.assertEquals(dates[i], new_dates[i])

        self.assertEquals(to_date, new_dates[-3])
        self.assertEquals(dates[-2], new_dates[-2])
        self.assertEquals(dates[-1], new_dates[-1])

        # now test error checking
        from_date = new_dates[-3]
        to_date = from_date + timedelta(days = 12)
        success, msg = Receiver_Schedule.shift_date(from_date, to_date)
        self.assertEquals(False, success)
        self.assertEquals("Cannot shift date to or past other dates", msg)

