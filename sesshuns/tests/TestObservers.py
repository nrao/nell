from copy                      import copy
from django.test.client        import Client
from django.conf               import settings
from django.contrib.auth       import models as m

from test_utils                import BenchTestCase, timeIt
from sesshuns.models           import *
from sesshuns.httpadapters     import *
from sesshuns.utilities        import create_user
from utils                     import create_sesshun, fdata
from sesshuns.GBTCalendarEvent import CalEventPeriod
from TestObserversBase         import TestObserversBase

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
        self.failUnlessEqual(response.status_code, 302)
        s = first(Sesshun.objects.filter(id = self.s.id))
        self.assertEqual(s.status.enabled, True)

    @timeIt
    def test_toggle_observer(self):
        i_id = first(self.p.investigator_set.all()).id
        response = self.post(
            '/project/%s/investigator/%s/observer' % (self.p.pcode, i_id))
        self.failUnlessEqual(response.status_code, 302)
        i = first(Investigator.objects.filter(id = i_id))
        self.assertEqual(i.observer, True)

    @timeIt
    def test_toggle_required_friend(self):
        f_id = self.friend.id
        self.assertEquals(self.friend.required, False)
        response = self.post(
            '/project/%s/friend/%s/required' % (self.p.pcode, f_id))
        self.failUnlessEqual(response.status_code, 302)
        f = Friend.objects.get(id = f_id)
        self.assertEqual(f.required, True)
        response = self.post(
            '/project/%s/friend/%s/required' % (self.p.pcode, f_id))
        self.failUnlessEqual(response.status_code, 302)
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
        u = first(User.objects.filter(id = self.u.id))
        self.assertEqual(u.contact_instructions, data.get('contact_instructions'))

    def create_blackout(self):
        b             = Blackout(user = self.u)
        b.start       = datetime(2009, 1, 1)
        b.end         = datetime(2009, 12, 31)
        b.repeat      = first(Repeat.objects.all())
        b.description = "This is a test blackout."
        b.save()
        return b

    def create_blackout_for_project(self):
        b             = Blackout(project = self.p)
        b.start       = datetime(2009, 1, 1)
        b.end         = datetime(2009, 12, 31)
        b.repeat      = first(Repeat.objects.all())
        b.description = "This is a test blackout for a project."
        b.save()
        return b

    def test_blackout_form(self):

        # user blackout
        response = self.get('/profile/%s/blackout/' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Blackout for dss account" in response.content)

        b = self.create_blackout()
        response = self.get('/profile/%s/blackout/%s/' % (self.u.id, b.id))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(b.description in response.content)

        # project blackout
        response = self.get('/project/%s/blackout/' % self.p.pcode)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("Blackout for mike" in response.content)

        b = self.create_blackout_for_project()
        response = self.get('/project/%s/blackout/%s/' % (self.p.pcode, b.id))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(b.description in response.content)

    @timeIt
    def test_blackout(self):
        # create a blackout
        b     = self.create_blackout()
        start = datetime(2009, 1, 1)
        end   = datetime(2009, 1, 31)
        until = datetime(2010, 1, 31)
        data = {'start'       : start.date().strftime("%m/%d/%Y")
              , 'start_time'   : start.time().strftime("%H:%M")
              , 'end'         : end.date().strftime("%m/%d/%Y")
              , 'end_time'     : end.time().strftime("%H:%M")
              , 'repeats'      : 'Once'
              , 'until'       : until.strftime("%m/%d/%Y")
              , 'until_time'   : until.strftime("%H:%M")
              , 'description' : "This is a test blackout."
              , '_method'     : "PUT"
                }

        # edit it
        response = self.post(
            '/profile/%s/blackout/%s/' % (self.u.id, b.id), data)
        b = first(Blackout.objects.filter(id = b.id))
        self.assertEqual(b.end_date.date().strftime("%m/%d/%Y") , data.get('end'))
        self.assertEqual(b.until.date().strftime("%m/%d/%Y") , data.get('until'))
        self.failUnlessEqual(response.status_code, 302)

        # delete it
        response = self.get(
            '/profile/%s/blackout/%s/' % (self.u.id, b.id)
          , {'_method' : 'DELETE'})
        self.failUnlessEqual(response.status_code, 302)
        # shouldn't this delete the blackout?
        b = first(Blackout.objects.filter(id = b.id))
        self.assertEqual(None, b)

        # create a new one
        data['end'] = date(2009, 5, 31).strftime("%m/%d/%Y")
        _ = data.pop('_method')
        response    = self.post(
            '/profile/%s/blackout/' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)
        b = first(self.u.blackout_set.all())
        self.assertEqual(b.end_date.date().strftime("%m/%d/%Y"), data.get('end'))
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
        b = first(Blackout.objects.filter(id = b.id))
        self.assertEqual(b.end_date.date().strftime("%m/%d/%Y") , data.get('end'))
        self.assertEqual(b.until.date().strftime("%m/%d/%Y") , data.get('until'))
        self.failUnlessEqual(response.status_code, 302)

        # now delete it
        response = self.get(
            '/project/%s/blackout/%s/' % (self.p.pcode, b.id)
          , {'_method' : 'DELETE'})
        self.failUnlessEqual(response.status_code, 302)
        # shouldn't this delete the blackout?
        b = first(Blackout.objects.filter(id = b.id))
        self.assertEqual(None, b)

        # now create one
        data['end'] = date(2009, 5, 31).strftime("%m/%d/%Y")
        _ = data.pop('_method')
        response    = self.post(
            '/project/%s/blackout/' % self.p.pcode, data)
        self.failUnlessEqual(response.status_code, 302)
        b = first(self.p.blackout_set.all())
        self.assertEqual(b.end_date.date().strftime("%m/%d/%Y"), data.get('end'))
        b.delete()

    @timeIt
    def test_get_period_day_time(self):

        # create a period
        s = create_sesshun()
        state = first(Period_State.objects.filter(abbreviation = 'S'))
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
        state = first(Period_State.objects.filter(abbreviation = 'S'))
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


