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

from copy                   import copy
from django.test.client     import Client
from django.conf            import settings
from django.contrib.auth    import models as m
from datetime               import datetime, timedelta, date
import time

from test_utils             import BenchTestCase, timeIt
from scheduler.models       import *
from scheduler.httpadapters import *
from scheduler.tests.utils  import create_sesshun, fdata, create_blackout
from users.utilities        import create_user
from users.GBTCalendarEvent import CalEventPeriod
from TestObserversBase      import TestObserversBase

class TestObservers(TestObserversBase):

    def test_profile(self):
        response = self.get('/profile/%s' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("mikes awesome project" in response.content)

    def test_project(self):
        response = self.get('/project/%s' % self.p.pcode)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Best Friend" in response.content)

    @timeIt
    def test_search(self):
        response = self.post('/search', {'search' : 'Test'})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("account" in response.content)

    @timeIt
    def test_toggle_session(self):
        response = self.post(
            '/project/%s/session/%s/enable' % (self.p.pcode, self.s.id))
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = self.s.id)
        self.assertEqual(s.status.enabled, True)

    @timeIt
    def test_toggle_observer(self):
        i_id = self.p.investigator_set.all()[0].id
        response = self.post(
            '/project/%s/investigator/%s/observer' % (self.p.pcode, i_id))
        self.failUnlessEqual(response.status_code, 200)
        i = Investigator.objects.get(id = i_id)
        self.assertEqual(i.observer, True)

    @timeIt
    def test_toggle_required_friend(self):
        f_id = self.friend.id
        self.assertEquals(self.friend.required, False)
        response = self.post(
            '/project/%s/friend/%s/required' % (self.p.pcode, f_id))
        self.failUnlessEqual(response.status_code, 200)
        f = Friend.objects.get(id = f_id)
        self.assertEqual(f.required, True)
        response = self.post(
            '/project/%s/friend/%s/required' % (self.p.pcode, f_id))
        self.failUnlessEqual(response.status_code, 200)
        f = Friend.objects.get(id = f_id)
        self.assertEqual(f.required, False)

    def test_dynamic_contact_form(self):
        response = self.get('/profile/%s/dynamic_contact' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_dynamic_contact_save(self):
        data = {'contact_instructions' : "I'll be at Bob's house."}
        response = self.post('/profile/%s/dynamic_contact' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)
        u = User.objects.get(id = self.u.id)
        self.assertEqual(u.contact_instructions, data.get('contact_instructions'))

    def create_blackout(self):
        b = create_blackout(user = self.u,
                            start = datetime(2009, 1, 1),
                            end = datetime(2009, 12, 31),
                            repeat = 'Once',
                            description = "This is a test blackout.")
        return b

    def create_blackout_for_project(self):
        b = create_blackout(project = self.p,
                            start = datetime(2009, 1, 1),
                            end = datetime(2009, 12, 31),
                            repeat = 'Once',
                            description = "This is a test blackout for a project.")
        return b

    def test_blackout_form(self):

        # user blackout
        response = self.get('/profile/%s/blackout/' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Blackout for dss account" in response.content)

        b = self.create_blackout()
        response = self.get('/profile/%s/blackout/%s/' % (self.u.id, b.id))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(b.getDescription() in response.content)
        self.assertTrue(b.getRepeat() in response.content)

        # project blackout
        response = self.get('/project/%s/blackout/' % self.p.pcode)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Blackout for mike" in response.content)

        b = self.create_blackout_for_project()
        response = self.get('/project/%s/blackout/%s/' % (self.p.pcode, b.id))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(b.getDescription() in response.content)
        self.assertTrue(b.getRepeat() in response.content)

    @timeIt
    def test_blackout(self):
        # create a blackout
        b     = self.create_blackout()
        start = datetime(2009, 1, 1)
        end   = datetime(2009, 1, 31)
        until = datetime(2010, 1, 31)
        data = {'start'       : start.date().strftime("%m/%d/%Y")
              , 'start_time'  : start.time().strftime("%H:%M")
              , 'end'         : end.date().strftime("%m/%d/%Y")
              , 'end_time'    : end.time().strftime("%H:%M")
              , 'repeats'     : 'Once'
              , 'until'       : until.strftime("%m/%d/%Y")
              , 'until_time'  : until.strftime("%H:%M")
              , 'description' : "This is a test blackout."
              , '_method'     : "PUT"
                }

        # edit it
        response = self.post(
            '/profile/%s/blackout/%s/' % (self.u.id, b.id), data)
        b = Blackout.objects.get(id = b.id)
        self.assertEqual(b.getEndDate().date().strftime("%m/%d/%Y") , data.get('end'))
        self.assertEqual(b.getUntil().date().strftime("%m/%d/%Y") , data.get('until'))
        self.failUnlessEqual(response.status_code, 302)

        # delete it
        response = self.get(
            '/profile/%s/blackout/%s/' % (self.u.id, b.id)
          , {'_method' : 'DELETE'})
        self.failUnlessEqual(response.status_code, 302)
        # shouldn't this delete the blackout?
        try:
            b = Blackout.objects.get(id = b.id)
        except Blackout.DoesNotExist:
            b = None
        self.assertEqual(None, b)

        # create a new one
        data['end'] = date(2009, 5, 31).strftime("%m/%d/%Y")
        _ = data.pop('_method')
        response    = self.post(
            '/profile/%s/blackout/' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)
        b = self.u.blackout_set.all()[0]
        self.assertEqual(b.getEndDate().date().strftime("%m/%d/%Y"), data.get('end'))
        b.delete()

        # create another new one?
        data['until'] = ''
        response    = self.post(
            '/profile/%s/blackout/' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)

    @timeIt
    def test_blackout2(self):
        b     = self.create_blackout()
        start = datetime(2009, 1, 1)
        end   = datetime(2009, 1, 31)
        until = datetime(2010, 1, 31)
        b.initialize(tz     = 'UTC',
                     start  = start,
                     end    = end,
                     repeat = Repeat.objects.get(repeat = 'Once'),
                     until  = until)
        data = {'start'       : start.date().strftime("%m/%d/%Y")
              , 'start_time'   : start.time().strftime("%H:%M")
              , 'end'         : end.date().strftime("%m/%d/%Y")
              , 'end_time'     : end.time().strftime("%H:%M")
              , 'repeats'      : 'Once'
              , 'until'       : until.strftime("%m/%d/%Y")
              , 'until_time'   : until.strftime("%H:%M")
              , 'description' : "This is a test blackout."
                }

        response = self.post(
            '/profile/%s/blackout/%s/' % (self.u.id, b.id), data)
        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue("ERROR" not in response.content)

        # test that a blackout can't have a missing end date
        data['end'] = None
        data['end_time'] = None
        response = self.post(
            '/profile/%s/blackout/%s/' % (self.u.id, b.id), data)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("ERROR" in response.content)

    @timeIt
    def test_blackout3(self):
        "Like test_blackout, but for a project"

        # create an initial blackout
        b     = self.create_blackout_for_project()
        start = datetime(2009, 1, 1)
        end   = datetime(2009, 1, 31)
        until = datetime(2010, 1, 31)
        b.initialize(tz     = 'UTC',
                     start  = start,
                     end    = end,
                     repeat = Repeat.objects.get(repeat = 'Once'),
                     until  = until)
        data = {'start'       : start.date().strftime("%m/%d/%Y")
              , 'start_time'   : start.time().strftime("%H:%M")
              , 'end'         : end.date().strftime("%m/%d/%Y")
              , 'end_time'     : end.time().strftime("%H:%M")
              , 'repeats'      : 'Once'
              , 'until'       : until.strftime("%m/%d/%Y")
              , 'until_time'   : until.strftime("%H:%M")
              , 'description' : "This is a test project blackout."
              , '_method'     : "PUT"
                }

        # now edit it
        response = self.post(
            '/project/%s/blackout/%s/' % (self.p.pcode, b.id), data)
        b = Blackout.objects.get(id = b.id)
        self.assertEqual(b.getEndDate().date().strftime("%m/%d/%Y") , data.get('end'))
        self.assertEqual(b.getUntil().date().strftime("%m/%d/%Y") , data.get('until'))
        self.failUnlessEqual(response.status_code, 302)

        # now delete it
        response = self.get(
            '/project/%s/blackout/%s/' % (self.p.pcode, b.id)
          , {'_method' : 'DELETE'})
        self.failUnlessEqual(response.status_code, 302)
        # shouldn't this delete the blackout?
        try:
            b = Blackout.objects.get(id = b.id)
        except Blackout.DoesNotExist:
            b = None
        self.assertEqual(None, b)

        # now create one
        data['end'] = date(2009, 5, 31).strftime("%m/%d/%Y")
        _ = data.pop('_method')
        response    = self.post(
            '/project/%s/blackout/' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 302)
        b = self.p.blackout_set.all()[0]
        self.assertEqual(b.getEndDate().date().strftime("%m/%d/%Y"), data.get('end'))
        b.delete()

    @timeIt
    def test_get_period_day_time(self):

        # create a period
        s = create_sesshun()
        state = Period_State.objects.get(abbreviation = 'S')
        p = Period(session = s
                 , start = datetime(2009, 9, 9, 12)
                 , duration = 1.0
                 , state = state)
        p.save()
        day = datetime(2009, 9, 9)

        # make sure it comes back in the correct day for UTC
        data = { 'start': day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz'   : 'UTC' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 9, 0, 0), [CalEventPeriod(p)]),
               (datetime(2009, 9, 10, 0, 0), []),
               (datetime(2009, 9, 11, 0, 0), [])]

        self.assertEqual(exp, calendar)

        # make sure it comes back in the correct day for EST
        data = { 'start': day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz'   : 'ET' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']

        exp = [(datetime(2009, 9, 9, 0, 0), [CalEventPeriod(p)]),
               (datetime(2009, 9, 10, 0, 0), []),
               (datetime(2009, 9, 11, 0, 0), [])]

        self.assertEqual(exp, calendar)

        # clean up
        p.remove() #delete()
        s.delete()

    @timeIt
    def test_get_period_day_time2(self):

        # create a period
        s = create_sesshun()
        state = Period_State.objects.get(abbreviation = 'S')
        p = Period(session = s
                 , start = datetime(2009, 9, 2, 1)
                 , duration = 6.0
                 , state = state)
        p.save()
        day = datetime(2009, 9, 1)

        # make sure it comes back in the correct day for UTC
        data = { 'start' : day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz' : 'UTC' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 1), []),
               (datetime(2009, 9, 2), [CalEventPeriod(p)]),
               (datetime(2009, 9, 3), [])]
        self.assertEqual(exp, calendar)

        # make sure it comes back in the correct day for EST
        data = { 'start' : day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz' : 'ET' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']

        day1 = datetime(2009, 9, 1)
        day2 = datetime(2009, 9, 2)
        day3 = datetime(2009, 9, 3)
        exp  = [(day1, [CalEventPeriod(p, p.start < day1, p.end() > day2, True, 'ET')]),
                (day2, [CalEventPeriod(p, p.start < day2, p.end() > day3, True, 'ET')]),
                (day3, [])]
        self.assertEqual(exp, calendar)

        # show the cutoff: '(..)'
        data = { 'start' : day.strftime("%m/%d/%Y")
               , 'days' : 1
               , 'tz' : 'ET' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        day1 = datetime(2009, 9, 1)
        ev1 = CalEventPeriod(p, p.start < day1, p.end() > (day1 + timedelta(1)), True, 'ET')
        exp = [(day1, [ev1])]
        self.assertEqual(exp, calendar)

        # clean up
        p.remove() #delete()
        s.delete()

    def test_create_user(self):
        "Stick Paul in the DSS DB"

        pauls = User.objects.filter(last_name = "Marganian")
        self.assertEqual(0, len(pauls))

        create_user('pmargani')

        pauls = User.objects.filter(last_name = "Marganian")
        self.assertEqual(1, len(pauls))
        paul = pauls[0]
        self.assertEqual(821, paul.pst_id)

        paul.delete()
        pauls = User.objects.filter(last_name = "Marganian")
        self.assertEqual(0, len(pauls))

    def test_event(self):

        start = datetime(2011, 8, 1)
        end   = datetime(2011, 9, 1)

        # what a pain in the ass: need to convert times to floats
        fmt = "%Y-%m-%d %H-%M-%S"
        startStr = start.strftime(fmt)
        endStr = end.strftime(fmt)
        data = { 'start' : time.mktime(time.strptime(startStr, fmt))
               , 'end'   : time.mktime(time.strptime(endStr,   fmt))
               }
        response = self.get('/project/%s/events' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 200)
        exp = [{"className": "semester", "start": "2012-02-01T00:00:00", "id": 1, "title": "Start of 12A"}
             , {"className": "semester", "start": "2012-08-01T00:00:00", "id": 2, "title": "Start of 12B"}]
        result = eval(response.content)
        self.assertEquals(result, exp)     

        # now add a user w/ reservations and blackouts
        # (oops, it only grabs UPCOMING reservations, so we
        # can't test the reservations!!!)
        dana = User(first_name = "Dana"
                          , last_name = "Balser"
                          , pst_id = 18
                           )
        dana.save()
        i =  Investigator(project = self.p
                        , user    = dana 
                         )
        i.save()
        b = create_blackout(user   = dana,
                            start  = start + timedelta(days = 2),
                            end    = start + timedelta(days = 7),
                            repeat = 'Once')
        # then a period
        pa = Period_Accounting(scheduled = 3.0)
        pa.save()
        p = Period(session = self.s
                 , start = start + timedelta(days = 3)
                 , duration = 3.0
                 , state = Period_State.get_state('S')
                 , accounting = pa
                  )
        p.save()

        # now see what we get
        response = self.get('/project/%s/events' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 200)
        exp = [{"className": "blackout",
                "start": "2011-08-03T00:00:00+00:00",
                "end": "2011-08-07T23:45:00+00:00",
                "title": "Dana Balser: blackout"}
             , {"className": "period",
                "start": "2011-08-04T00:00:00+00:00",
                "end": "2011-08-04T03:00:00",
                "title": "Observing Low Frequency With No RFI"}
             , {"className": "semester",
                "start": "2012-02-01T00:00:00",
                "title": "Start of 12A"}
             , {"className": "semester",
                "start": "2012-08-01T00:00:00",
                "title": "Start of 12B"}
             ]

        result = eval(response.content)
        # now, since we don't have control of reservations, if there is a reservation, remove it
        filteredResult = [r for r in result if not r.has_key('className') or r['className'] != 'reservation']
        # we have to remove the id as well, since there's no guarantee what this will be
        for r in filteredResult:
            r.pop('id')
        self.assertEquals(len(filteredResult), len(exp))
        for r in filteredResult:
            self.assertTrue(r in exp)

    def test_dates_not_schedulable(self):

        def getUnavilDct(bs = 'false'
                       , no_enabled = 'false'
                       , no_authorized = 'false'
                       , prescheduled = 'false'
                       , date = '2011-08-01'):
            "help function producing expected results."               
            exp = '{"prescheduled": %s, "blackedout": %s, "pcode": "mike", "no_incomplete_sessions": false, "project_complete": false, "date": "%s", "no_receivers": false, "no_enabled_sessions": %s, "no_authorized_sessions": %s}' % (prescheduled, bs, date, no_enabled, no_authorized)
            return exp

        start = datetime(2011, 8, 1)
        dayTwo = start + timedelta(days = 1)
        end   = datetime(2011, 8, 4)
        allDates = [{'start' : '2011-08-0%dT00:00:00' % i} for i in range(1,4)]

        # what a pain in the ass: need to convert times to floats
        fmt = "%Y-%m-%d %H-%M-%S"
        startStr  = start.strftime(fmt)
        dayTwoStr = dayTwo.strftime(fmt)
        endStr    = end.strftime(fmt)
        startTime  = time.mktime(time.strptime(startStr, fmt))
        dayTwoTime = time.mktime(time.strptime(dayTwoStr, fmt))
        endTime    = time.mktime(time.strptime(endStr,   fmt))
        data = { 'start' : startTime
               , 'end'   : endTime
               , 'past'  : True
               }
        response = self.get('/project/%s/unavailable' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 200)

        # none of the dates will be available
        result = eval(response.content)
        self.assertEquals(result, allDates)     

        # because the one session is not schedulable
        response = self.get('/project/%s/unavailable/details' % self.p.pcode, {'date' : startTime})

        self.failUnlessEqual(response.status_code, 200)
        exp = getUnavilDct(no_enabled = "true", no_authorized = "true")
        self.assertEquals(exp, response.content)     

        # now make the session enabled, and see how things change 
        self.s.status.enabled = self.s.status.authorized = True
        self.s.status.save()

        response = self.get('/project/%s/unavailable' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 200)

        # none of the dates will be UNavailable
        result = eval(response.content)
        self.assertEquals([], result) 

        response = self.get('/project/%s/unavailable/details' % self.p.pcode, {'date' : startTime})

        exp = getUnavilDct()
        self.assertEqual(exp, response.content)

        # now modify the observer and give them blackouts so that 
        # the project can't be observed
        self.i.observer = True
        self.i.save()
        self.u.sanctioned = True
        self.u.save()
        b = Blackout(user = self.u)
        b.initialize(tz = 'UTC',
                     start = start + timedelta(days = 1),
                     end   = start + timedelta(days = 7)
                    )
       
        # see how this messes things up
        response = self.get('/project/%s/unavailable' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 200)
        # the last two dates are blacked out 
        result = eval(response.content)
        self.assertEquals(allDates[1:], result) 

        # details on first available day
        response = self.get('/project/%s/unavailable/details' % self.p.pcode, {'date' : startTime})
        exp = getUnavilDct()
        self.assertEqual(exp, response.content)

        # details on first UNavailable day
        response = self.get('/project/%s/unavailable/details' % self.p.pcode, {'date' : dayTwoTime})
        exp = getUnavilDct(bs = 'true', date = "2011-08-02")
        self.assertEqual(exp, response.content)

        # Now, mess up the first day with a period from a different project
        p2 = self.create_project('mark')
        p2.save()
        s2 = self.create_session()
        s2.project = p2
        s2.save()
        pa = Period_Accounting(scheduled = 3.0)
        pa.save()
        p = Period(session = s2
                 , start = start 
                 , duration = 25.0 # should block out 1st day, but not 2cd
                 , state = Period_State.get_state('S')
                 , accounting = pa
                  )
        p.save()

        response = self.get('/project/%s/unavailable' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 200)
        # all dates are unavailable again 
        result = eval(response.content)
        self.assertEquals(allDates, result) 

        # details on first day
        response = self.get('/project/%s/unavailable/details' % self.p.pcode, {'date' : startTime})
        exp = getUnavilDct(prescheduled = 'true')
        self.assertEqual(exp, response.content)

        # details on second day
        response = self.get('/project/%s/unavailable/details' % self.p.pcode, {'date' : dayTwoTime})
        exp = getUnavilDct(bs = 'true', date = "2011-08-02")
        self.assertEqual(exp, response.content)

