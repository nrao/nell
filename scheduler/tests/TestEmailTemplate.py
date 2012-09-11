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

from test_utils              import NellTestCase
from utils                   import create_sesshun
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestEmailTemplate(NellTestCase):

    def setUp(self):
        super(TestEmailTemplate, self).setUp()

        # TBF: our initial DB is lacking some future semesters
        for year in range(13, 33):
            for sem in ['A', 'B']:
                s = Semester(semester = "%s%s" % (year, sem))
                s.save()

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

