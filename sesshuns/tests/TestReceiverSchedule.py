from datetime            import datetime
from django.test.client  import Client

from sesshuns.httpadapters   import *
from sesshuns.models         import *
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

    @timeIt
    def test_receivers_schedule(self):
        startdate = datetime(2009, 4, 6, 12)
        response = self.client.get('/receivers/schedule',
                                   {"startdate" : startdate,
                                    "duration" : 7})
        self.failUnlessEqual(response.status_code, 200)
        #expected = '{"diff": [{"down": [], "up": ["RRI", "342", "450"], "day": "04/06/2009"}, {"down": ["RRI"], "up": ["600"], "day": "04/11/2009"}], "receivers": ["RRI", "342", "450", "600", "800", "1070", "L", "S", "C", "X", "Ku", "K", "Ka", "Q", "MBA", "Z", "Hol", "KFPA"], "maintenance": [{"wdefault": null, "wstart": null, "handle": "Maintenance (GBT-M09A) 0", "wend": null, "state": "", "moc_ack": false, "windowed": false, "sscore": null, "cscore": 0.0, "duration": 6.0, "lst": "09:10:57", "session": {"grade": 4.0, "nighttime": false, "transit": false, "sem_time": 100.5, "lst_ex": "", "id": 1, "pcode": "GBT-M09A", "authorized": false, "type": "open", "remaining": 100.5, "total_time": 100.5, "complete": false, "project_complete": "No", "PSC_time": 100.5, "name": "Maintenance", "science": "radar", "orig_ID": 0, "enabled": false, "xi_factor": 1.0, "receiver": "", "backup": false}, "time": "00:00", "date": "2009-04-30", "receivers": "", "forecast": null, "backup": false, "id": 1, "stype": "O"}], "schedule": {"04/11/2009": ["342", "450", "600"], "04/06/2009": ["RRI", "342", "450"]}}'
        expected = '{"diff": [{"down": [], "up": ["RRI", "342", "450"], "day": "04/06/2009"}, {"down": ["RRI"], "up": ["600"], "day": "04/11/2009"}], "receivers": ["RRI", "342", "450", "600", "800", "1070", "L", "S", "C", "X", "Ku", "K", "Ka", "Q", "MBA", "Z", "Hol", "KFPA"], "maintenance": [], "schedule": {"04/11/2009": ["342", "450", "600"], "04/06/2009": ["RRI", "342", "450"]}}'

        self.assertEqual(expected, response.content)

    @timeIt
    def test_change_schedule(self):
        "The simplest change: new change date at the end"

        # get the current schedule
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())

        # now add a rcvr change latter in time
        last_date = dates[-1]
        new_date = last_date + timedelta(days = 5)
        available = schedule[last_date]
        S = available[0]
        L = Receiver.get_rcvr("L")
        # take down S and put up L
        Receiver_Schedule.change_schedule(new_date, [L], [S])

        # make sure it changed appropriately
        new_schd = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates = sorted(new_schd.keys())
        self.assertEquals(len(dates) + 1, len(new_dates))
        # nothing before the change changed?
        for i, dt in enumerate(dates):
            self.assertEquals(dt, new_dates[i])
            self.assertEquals(schedule[dt], new_schd[new_dates[i]])

        # now make sure the new change makes sense
        X = Receiver.get_rcvr("X")
        C = Receiver.get_rcvr("C")
        rcvrs = [C, X, L]
        self.assertEquals(rcvrs, new_schd[new_date])

    def test_change_schedule_2(self):
        "A more complicated change"

        # get the current schedule
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())
        #for dt in dates:
        #    print dt, [r.abbreviation for r in schedule[dt]]

        # now add a rcvr change on one of these given days
        change_date = dates[-3]
        #new_date = last_date + timedelta(days = 5)
        available = schedule[change_date]

        L = available[1]
        r342 = Receiver.get_rcvr("342")
        # take down L and put up 342
        Receiver_Schedule.change_schedule(change_date, [r342], [L])

        # make sure it changed appropriately
        new_schd = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates = sorted(new_schd.keys())
        self.assertEquals(len(dates), len(new_dates))
        #print "new: "
        #for dt in new_dates:
        #    print [r.abbreviation for r in new_schd[dt]]

        # nothing before the change changed?
        for i, dt in enumerate(dates):
            if dt < change_date:
                self.assertEquals(dt, new_dates[i])
                self.assertEquals(schedule[dt], new_schd[new_dates[i]])

        # now make sure the new change makes sense
        # get last 3 dates
        changed_dates = dates[len(dates)-3:]
        X = Receiver.get_rcvr("X")
        C = Receiver.get_rcvr("C")
        S = Receiver.get_rcvr("S")
        r1070 = Receiver.get_rcvr("1070")
        r800 = Receiver.get_rcvr("800")
        changed_schd = {changed_dates[0] : [r1070, r342, r800]
                      , changed_dates[1] : [C, r342, r800]
                      , changed_dates[2] : [C, X, r342, r800]}
        for dt in changed_dates:
            self.assertEquals(changed_schd[dt], new_schd[dt])

    def test_change_schedule_3(self):
        "More then one change on a given date. "

        # get the current schedule
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())
        #for dt in dates:
        #    print dt, [r.abbreviation for r in schedule[dt]]

        # now add a rcvr change latter in time
        last_date = dates[-1]
        new_date = last_date + timedelta(days = 5)
        available = schedule[last_date]
        S = available[0]
        C = available[1]
        L = Receiver.get_rcvr("L")
        Q = Receiver.get_rcvr("Q")
        X = Receiver.get_rcvr("X")
        # I. take down S & C and put up L & Q
        Receiver_Schedule.change_schedule(new_date, [L, Q], [S, C])

        # make sure it changed appropriately
        new_schd = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates = sorted(new_schd.keys())
        self.assertEquals(len(dates) + 1, len(new_dates))
        # nothing before the change changed?
        for i, dt in enumerate(dates):
            self.assertEquals(dt, new_dates[i])
            self.assertEquals(schedule[dt], new_schd[new_dates[i]])

        # now make sure the new change makes sense
        rcvrs = sorted([L, Q, X])
        rcvrs = sorted([r.abbreviation for r in [L, Q, X]])
        new_rs = sorted([r.abbreviation for r in new_schd[new_date]])
        self.assertEquals(rcvrs, new_rs)

        # now specify this same change to this date - nothing should happen
        s, msg = Receiver_Schedule.change_schedule(new_date, [L, Q], [S, C])
        self.assertEquals(True, s)
        self.assertEquals(None, msg)
        new_schd_2 = Receiver_Schedule.extract_schedule(startdate = startdate)
        self.assertEquals(new_schd, new_schd_2)
        new_dates_2 = sorted(new_schd_2.keys())
        #for dt in new_dates_2:
        #    print dt, [r.abbreviation for r in new_schd_2[dt]]

        # II. make a slight modification - don't put up Q and don't put down C
        s, msg = Receiver_Schedule.change_schedule(new_date, [L], [S])
        self.assertEquals(True, s)
        self.assertEquals(None, msg)
        new_schd_3 = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates_3 = sorted(new_schd_3.keys())
        #for dt in new_dates_3:
        #    print dt, [r.abbreviation for r in new_schd_3[dt]]
        self.assertEquals(len(new_dates), len(new_dates_3))

        # now make sure the new change makes sense
        rcvrs = sorted([r.abbreviation for r in [L, C, X]])
        new_rs = sorted([r.abbreviation for r in new_schd_3[new_date]])
        self.assertEquals(rcvrs, new_rs)


    @timeIt
    def test_change_receiver_schedule(self):
        # last rcvr change:
        # 2009-05-11 00:00:00 [u'S', u'C', u'X']

        # successful change
        startdate = datetime(2009, 5, 16)
        response = self.client.post('/receivers/change_schedule',
                                   {"startdate" : startdate
                                  , "up" : "L"
                                  , "down" : "S"
                                   })
        self.failUnlessEqual(response.status_code, 200)

        # do something stupid
        response = self.client.post('/receivers/change_schedule',
                                   {"startdate" : startdate
                                  , "up" : "Bob"
                                  , "down" : "K"
                                   })
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Unrecognized receiver: Bob" in response.content)
        return

        # TBF: are these going to cause errors?
        response = self.client.post('/receivers/change_schedule',
                                   {"startdate" : startdate
                                  , "up" : "Q"
                                  , "down" : "K"
                                   })
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Receiver Rcvr18_26 cannot come down" \
                              in response.content)

        # get the current schedule
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())
        #for dt in dates:
        #    print dt, [r.abbreviation for r in schedule[dt]]

        # specifying something as going that is already up does not cause
        # an error
        response = self.client.post('/receivers/change_schedule',
                                   {"startdate" : startdate
                                  , "up" : "S"
                                  , "down" : "C"
                                   })
        self.failUnlessEqual(response.status_code, 200)

    def test_delete_date(self):
        # get the current schedule
        startdate = datetime(2009, 4, 6, 12)
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        dates = sorted(schedule.keys())
        #for dt in dates:
        #    print dt, [r.abbreviation for r in schedule[dt]]

        # delete a date
        Receiver_Schedule.delete_date(dates[-3])

        # get the new schedule
        new_schedule = Receiver_Schedule.extract_schedule(startdate = startdate)
        new_dates = sorted(new_schedule.keys())

        # should be missing this deleted date
        self.assertEquals(len(new_dates) + 1, len(dates))
        # but schedule should'nt have changed up to this date
        for dt in dates[:4]:
            self.assertEquals(new_schedule[dt], schedule[dt])
        # does the change make sense?
        new_rs = []
        for dt in new_dates[len(new_dates)-3:]:
            new_rs.append(sorted([r.abbreviation for r in new_schedule[dt]]))
        exp_rs = [['1070', '800', 'L']
                , ['800',  'C',   'L']
                , ['800',  'C',   'X']]
        self.assertEquals(exp_rs, new_rs)

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

