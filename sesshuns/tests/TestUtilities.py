from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from sesshuns.models         import *
from sesshuns.utilities      import *
from utils                   import create_sesshun

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
        proj = first(Project.objects.all())

        # create a bunch of investigators for it:
        invs = [("PI", "PI", True, False, False, 821) # Paul
              , ("PC", "PC", False, True, False, 554) # Amy
              , ("obs1", "obs1", False, False, True, 3253) # Mark
              , ("obs2", "obs2", False, False, True, 3680) # Ray
                ]

                
        emails = self.setupInvestigators(invs, proj)
          
        pi, pc, ci, ob = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        self.assertEqual(emails[1], pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[2][0], emails[3][0]], ob)

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
          
        pi, pc, ci, ob = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        pc_emails = emails[1]
        pc_emails.extend(emails[0])
        self.assertEqual(pc_emails, pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[1][0], emails[2][0]], ob)
