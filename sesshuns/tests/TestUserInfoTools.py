from tools.database import UserNames
from scheduler.models         import *
from test_utils              import NellTestCase

class TestUserNames(NellTestCase):

    def test_findUserMatches(self):

        # setup - create a DSS user that matches someone you KNOW
        # exists in the PST
        hacker = User(last_name = "Marganian"
                    , first_name = "Paul"
                    , role = Role.objects.all()[0]
                     )
        hacker.save()
 
        # write results to a file
        f = open("TestUserNames.txt", 'w')
        un = UserNames.UserNames(output_file = f)
        un.findUserMatches()
        f.close()

        # check file for results
        f = open("TestUserNames.txt", 'r')
        lines = f.readlines()
        self.assertEqual(4, len(lines))
        self.assertTrue("User: Marganian, Paul, Projects:" in lines[1])
        self.assertTrue("pmargani   821  True pmargani@nrao.edu" in lines[3])

        # clean up
        hacker.delete()

    def test_findReportUserInfo(self):

        # setup - create a DSS user that matches someone you KNOW
        # exists in the PST
        hacker = User(last_name = "Marganian"
                    , first_name = "Paul"
                    , pst_id = 821
                    , role = Role.objects.all()[0]
                     )
        hacker.save()
        # and setup someone who does not exist
        professional_software_engineer = User(last_name = "Hocus"
                                            , first_name = "Pocus"
                                            , role = Role.objects.all()[0]
                                             )
        professional_software_engineer.save()                                             
        
        # write results to a file
        f = open("TestUserNames.txt", 'w')
        un = UserNames.UserNames(output_file = f)
        un.reportUserInfo()
        f.close()

        # check file for results
        f = open("TestUserNames.txt", 'r')
        lines = f.readlines()
        self.assertEqual(9, len(lines))
        self.assertTrue("len(users):  2" in lines[2])
        self.assertTrue("len(noPstId):  1" in lines[3])
        self.assertTrue("len(matched):  1" in lines[4])
        self.assertTrue("len(mismatched):  0" in lines[5])

        # clean up
        hacker.delete()
        professional_software_engineer.delete()

    def test_assignPstIds(self):

        # setup - create a DSS user that matches someone you KNOW
        # exists in the PST
        hacker = User(last_name = "Marganian"
                    , first_name = "Paul"
                    #, pst_id = 821
                    , role = Role.objects.all()[0]
                     )
        hacker.save()
        # and setup someone who does not exist
        professional_software_engineer = User(last_name = "Hocus"
                                            , first_name = "Pocus"
                                            , role = Role.objects.all()[0]
                                             )
        professional_software_engineer.save()                                             
        
        # write results to a file
        f = open("TestUserNames.txt", 'w')
        un = UserNames.UserNames(output_file = f)
        un.assignPstIds()
        f.close()

        # check file for results
        f = open("TestUserNames.txt", 'r')
        lines = f.readlines()
        self.assertEqual(12, len(lines))
        self.assertTrue("Found pst_id for user:  Marganian, Paul pmargani 821" in lines[1])
        self.assertTrue("Did NOT find pst_id for user:  Hocus, Pocus" in lines[3])

        # clean up
        hacker.delete()
        professional_software_engineer.save()

