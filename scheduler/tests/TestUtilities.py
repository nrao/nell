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

from datetime                import timedelta

from test_utils              import BenchTestCase, timeIt
from scheduler.models        import *
from scheduler.utilities     import *
from utils                   import create_sesshun, setupElectives, setupWindows

class TestUtilities(BenchTestCase):

    def setupInvestigators(self, invs, proj):
        "Creates investigators, and returns expected emails."

        emails = []
        obs = Role.objects.get(role = "Observer")
        for fn, ln, pi, pc, ob, id in invs:
            u = User(first_name = fn
                   , last_name  = ln
                   , role = obs
                   , pst_id = id # give them sombody's email
                    )
            u.save()
            inv = Investigator(user = u
                             , project = proj
                             , principal_investigator = pi
                             , principal_contact = pc
                             , observer = ob
                              )
            inv.save() 
            emails.append(sorted(u.getEmails()))
        return emails  
       

    def test_getInvestigators(self):

        # get the project we assume is already in the DB
        proj = Project.objects.all()[0]

        # create a bunch of investigators for it:
        invs = [("PI", "PI", True, False, False, 821) # Paul
              , ("PC", "PC", False, True, False, 554) # Amy
              , ("obs1", "obs1", False, False, True, 3253) # Mark
              , ("obs2", "obs2", False, False, True, 3680) # Ray
                ]

                
        emails = self.setupInvestigators(invs, proj)
          
        pi, pc, ci, ob, fs = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        self.assertEqual(emails[1], pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[2][0], emails[3][0]], ob)
        self.assertEqual([], fs)

        # try it again, overlapping roles
        for u in User.objects.all():
            u.delete()
        for i in Investigator.objects.all():
            i.delete()
        invs = [("PI", "PI", True, True, False, 821) # Paul
              , ("PC", "PC", False, True, True, 554) # Amy
              , ("obs1", "obs1", False, False, True, 3253) # Mark
              , ("obs2", "obs2", False, False, False, 3680) # Ray
                ]        
                
        emails = self.setupInvestigators(invs, proj)
          
        pi, pc, ci, ob, fs = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        pc_emails = list(emails[1])
        pc_emails.extend(emails[0])
        self.assertEqual(pc_emails, pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[1][0], emails[2][0]], ob)
        self.assertEqual([], fs)

        # now make some friends
        obs = Role.objects.get(role = "Observer")
        u = User(pst_id = 554, role = obs)
        u.save()
        f = Friend(user = u, project = proj)
        f.save()

        pi, pc, ci, ob, fs = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        self.assertEqual(pc_emails, pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[1][0], emails[2][0]], ob)
        self.assertEqual(emails[1], fs)

    @setupElectives
    def test_copy_elective(self):

        # finally, done with setup
        origNumWins = len(Elective.objects.all())

        # actually copy the window for testing
        copy_elective(self.elec.id, 1)

        newWins = Elective.objects.all().order_by("id")
        numWins = len(newWins)
        self.assertEquals(origNumWins + 1, numWins)

        ne = newWins[numWins-1]

        self.assertEquals(self.elec.session, ne.session)
        self.assertEquals(self.elec.complete, ne.complete)
        self.assertNotEqual(self.elec.periods.all(),ne.periods.all())
        self.assertEquals(len(self.elec.periods.all())
                        , len(ne.periods.all()))
        self.assertEquals([p.session.id for p in self.elec.periods.all()]
                        , [p.session.id for p in ne.periods.all()])


    @setupWindows
    def test_copy_window(self):

        origNumWins = len(Window.objects.all())

        # actually copy the window for testing
        copy_window(self.w.id, 1)

        newWins = Window.objects.all().order_by("id")
        numWins = len(newWins)
        self.assertEquals(origNumWins + 1, numWins)

        nw = newWins[numWins-1]

        self.assertEquals(self.w.session, nw.session)
        self.assertEquals(self.w.complete, nw.complete)
        self.assertEquals(self.w.total_time, nw.total_time)
        self.assertEquals(self.w.timeRemaining(), nw.timeRemaining())
        self.assertEquals(self.w.start(), nw.start())
        self.assertEquals(self.w.last_date(), nw.last_date())
        self.assertNotEqual(self.w.ranges(),nw.ranges())
        self.assertEquals(self.w.default_period.start
                        , nw.default_period.start)
        self.assertEquals(self.w.default_period.end()
                        , nw.default_period.end())
        self.assertNotEqual(self.w.default_period.id
                        , nw.default_period.id)
        self.assertNotEqual(self.w.periods.all(),nw.periods.all())
        self.assertEquals(len(self.w.periods.all())
                        , len(nw.periods.all()))
        self.assertEquals([p.session.id for p in self.w.periods.all()]
                        , [p.session.id for p in nw.periods.all()])

        # now publish the default period, see what happens
        self.default_period.publish()
        self.w = Window.objects.get(id = self.w.id)
        self.assertEqual(self.w.complete, True)
        self.assertEqual(self.w.timeRemaining(), 0.0)

        # make a copy of this in it's present state
        copy_window(self.w.id, 1)

        newWins = Window.objects.all().order_by("id")
        numWins = len(newWins)
        self.assertEquals(origNumWins + 2, numWins)

        nw = newWins[numWins-1]
        
        self.assertEquals(self.w.session, nw.session)
        self.assertEquals(self.w.complete, nw.complete)
        self.assertEquals(self.w.total_time, nw.total_time)
        self.assertEquals(self.w.timeRemaining(), nw.timeRemaining())
        self.assertEquals(self.w.start(), nw.start())
        self.assertEquals(self.w.last_date(), nw.last_date())
        self.assertNotEqual(self.w.ranges(),nw.ranges())
        self.assertEquals(self.w.default_period.start
                        , nw.default_period.start)
        self.assertEquals(self.w.default_period.end()
                        , nw.default_period.end())
        self.assertNotEqual(self.w.default_period.id
                        , nw.default_period.id)
        self.assertNotEqual(self.w.periods.all(),nw.periods.all())
        self.assertEquals(len(self.w.periods.all())
                        , len(nw.periods.all()))
        self.assertEquals([p.session.id for p in self.w.periods.all()]
                        , [p.session.id for p in nw.periods.all()])
        


