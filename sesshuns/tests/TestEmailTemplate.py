from test_utils              import NellTestCase
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestEmailTemplate(NellTestCase):

    def setUp(self):
        super(TestEmailTemplate, self).setUp()

        self.templates = [("Blank", "", "")
                   , ("First"
                   , "<pcode> is done"
                   , "Your project <pcode> is done.")
                   , ("Second"
                   , "<pcode> sucks"
                   , "Your project <pcode> sucks. Try it next semester: <start_next_semester>.")
                    ]
        for name, subj, body in self.templates:                    
            et = EmailTemplate(name = name
                             , subject = subj
                             , body = body)
            et.save()

    def assertTemplates(self, templates):

        p = Project.objects.all()[0]

        exp = {"Blank" : {"name" : "Blank", "subject" : "", "body" : ""}
             , "First" : 
               {"name" : "First"
              , "subject" : "%s is done" % p.pcode
              , "body" : "Your project %s is done." % p.pcode}
             , "Second" :
               {"name" : "%s" % "Second"
              , "subject" : "%s sucks" % p.pcode
              , "body" : "Your project %s sucks.  Try it next semester: " % p.pcode}
              }

        for t in templates:
            for field in ["name", "subject", "body"]:
                if field != 'body' and t["name"] != "Second": 
                    self.assertEquals(exp[t["name"]][field], t[field])

    def test_evaluate(self):

        ts = EmailTemplate.objects.all().order_by("name")
        p = Project.objects.all()[0]
        self.assertTemplates([t.evaluate(p) for t in ts])


    def test_get_templates(self):

        pcodes = [p.pcode for p in Project.objects.all()]
        templates = EmailTemplate.get_templates(pcodes)
        self.assertTemplates(templates)

