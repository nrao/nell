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

from test_utils                  import NellTestCase
from nell.tools.database         import DBReporter
from nell.scheduler.models       import Project
from nell.scheduler.httpadapters import ProjectHttpAdapter
from scheduler.tests.utils       import create_sesshun
import os

class TestDBReporter(NellTestCase):

    def test_reportProjectSummary(self):

        filename = "DBReporter.txt"
        db = DBReporter(quiet=True, filename = filename)

        # see what the report looks like w/ just one empty project
        db.reportProjectSummary(Project.objects.all())
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        self.assertEquals(49, len(lines))
        self.assertTrue("     09A     1          0" in lines[21])
        self.assertTrue("     09B     0          0" in lines[22])
        self.assertTrue("Total # of Projects: 1, Total Hrs:  0.00" in lines[2])
        self.assertTrue("GBT09A-001     0   0.00" in lines[-2])

        # now add a different project
        project = Project()
        project_adapter = ProjectHttpAdapter(project)
        pdata = {"semester"   : "09B"
               , "pcode"      : "GBT09B-047"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
               , "notes"      : "notes"
               , "schd_notes" : "scheduler's notes"
        }
        project_adapter.update_from_post(pdata)

        # make a session
        sesshun = create_sesshun()
        sesshun.allotment.total_time = 10.0
        sesshun.allotment.save()
        sesshun.original_id = 123
        sesshun.project = project
        sesshun.save()

        # init
        os.remove(filename)
       
        # now see what the report looks like
        db = DBReporter(quiet=True, filename = filename)
        db.reportProjectSummary(Project.objects.all())
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        self.assertEquals(50, len(lines))
        self.assertTrue("     09A     1          0" in lines[21])
        self.assertTrue("     09B     1       10.0" in lines[22])
        self.assertTrue("Total # of Projects: 2, Total Hrs: 10.00" in lines[2])
        self.assertTrue("GBT09A-001     0   0.00" in lines[-3])
        self.assertTrue("GBT09B-047     1  10.00                                                123" in lines[-2])
