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

from datetime            import datetime, timedelta
from django.test.client  import Client

from test_utils       import NellTestCase
from scheduler.models  import *
from utils            import *

class TestSemester(NellTestCase):

    def test_getFutureSemesters(self):
        dt = datetime(2010, 12, 25, 0, 0, 0)
        future = [s.semester for s in Semester.getFutureSemesters(dt)]
        self.assertEqual([u'11A', u'11B', u'12A', u'12B'], future[:4])

    def test_getPreviousSemesters(self):
        dt = datetime(2010, 12, 25, 0, 0, 0)
        previous = [s.semester for s in Semester.getPreviousSemesters(dt)]
        self.assertEqual([u'04A', u'05A', u'05B', u'05C', u'06A', u'06B'
                        , u'06C', u'07A', u'07B', u'07C', u'08A', u'08B'
                        , u'08C', u'09A', u'09B', u'09C', u'10A', u'10B'
                        , u'10C'], previous)

    def test_dates(self):

        # start and end dates for semesters follow a simple pattern:
        # before 11A:
        # yyA : (yy,  2, 1) to (yy,   5, 31) # 4 months 
        # yyB : (yy,  6, 1) to (yy,   9, 30) # 4 months
        # yyC : (yy, 10, 1) to (yy+1, 1, 31) # 4 months
        # 11A and 11B are fucked up:
        # 11A : (2011, 2, 1) to (2011, 6, 30) # 5 months 
        # 11B : (2011, 7, 1) to (2012, 1, 31) # 7 months
        # after 11B:
        # yyA : (yy,  2, 1) to (yy,   7, 31) # 6 months
        # yyB : (yy,  8, 1) to (yy+1, 1, 31) # 6 months
      
        # test the stuff before 11A
        sem = Semester.objects.filter(semester__gt = "05C"
            , semester__lt = "11A").order_by("semester")
        dts = [(s.semester
              , "%s" % s.start().strftime("%Y-%m-%d")
              , "%s" % s.end().strftime("%Y-%m-%d")) for s in sem]
        exp1 = []
        for y in range(2006, 2011):
            exp1.extend(self.getPre11Adates(y))
        for i in range(len(dts)):
            self.assertEqual(exp1[i], dts[i])

        # test the stuff after 11B - right now only two of them!
        # but set the test up to be extended anyways
        sem = Semester.objects.filter(semester__gt = "11B"
            , semester__lt = "13A").order_by("semester")
        dts = [(s.semester
              , "%s" % s.start().strftime("%Y-%m-%d")
              , "%s" % s.end().strftime("%Y-%m-%d")) for s in sem]
        exp2 = []
        for y in [2012]:
            exp2.extend(self.getPost11Bdates(y))
        for i in range(len(dts)):
            self.assertEqual(exp2[i], dts[i])

    def getPre11Adates(self, y):
        sem = str(y)[-2:]
        return [("%sA" % sem, '%d-02-01' % y, '%d-05-31' % y)
              , ("%sB" % sem, '%d-06-01' % y, '%d-09-30' % y)
              , ("%sC" % sem, '%d-10-01' % y, '%d-01-31' % (y+1))]

    def getPost11Bdates(self, y):
        sem = str(y)[-2:]
        return [("%sA" % sem, '%d-02-01' % y, '%d-07-31' %y)
              , ("%sB" % sem, '%d-08-01' % y, '%d-01-31' % (y+1))]

