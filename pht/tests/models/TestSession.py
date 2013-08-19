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

import simplejson as json
from django.test        import TestCase
from datetime           import datetime, timedelta
from pht.models         import *

class TestSession(TestCase):
    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json']

    def setUp(self):

        # too lazy to update the fixture, so adding new rx
        mba15 = Receiver(name = 'Rcvr_MBA1_5'
                       , abbreviation = 'MBA1.5'
                       , freq_hi = 100.0
                       , freq_low = 80.0
                         )
        mba15.save()

        # load the single proposal from the fixture
        self.proposal = Proposal.objects.get(pcode = "GBT12A-002")
        self.session = self.proposal.session_set.all().order_by('id')[0]

    def test_getTotalRequestedTime(self):

        self.assertEqual(21.0, self.session.getTotalRequestedTime())
        self.session.allotment.repeats = 2
        self.session.allotment.save()
        self.assertEqual(42.0, self.session.getTotalRequestedTime())
        self.session.allotment.repeats = 1
        self.session.allotment.save()

    def test_getTotalAllocatedTime(self):

        self.assertEqual(None, self.session.getTotalAllocatedTime())
        self.session.allotment.allocated_time = 21.0
        self.session.allotment.allocated_repeats = 1
        self.session.allotment.save()

        self.assertEqual(21.0, self.session.getTotalAllocatedTime())
        self.session.allotment.allocated_repeats = 2
        self.session.allotment.save()
        self.assertEqual(42.0, self.session.getTotalAllocatedTime())
        self.session.monitoring.outer_repeats = 3
        self.session.monitoring.save()
        self.assertEqual(42.0*3, self.session.getTotalAllocatedTime())

    def test_determineFreqCategory(self):
        self.assertEqual('LF', self.session.determineFreqCategory())
        # change it to high freq
        mba15 = Receiver.objects.get(abbreviation = 'MBA1.5')
        self.session.receivers.add(mba15)
        self.assertEqual('HF2', self.session.determineFreqCategory())

    def test_determineSessionType(self):
        self.assertEqual('Open - Low Freq'
                       , self.session.determineSessionType().type)

    def test_determineWeatherType(self):
        self.assertEqual('Poor'
                       , self.session.determineWeatherType().type)
        # change it to high freq
        mba15 = Receiver.objects.get(abbreviation = 'MBA1.5')
        self.session.receivers.add(mba15)
        self.assertEqual('Excellent', self.session.determineWeatherType().type)

    def test_genPeriods(self):

        # first make sure we don't crash when things
        # aren't setup
        r = self.session.genPeriods()
        ps = self.session.period_set.all().order_by('start')
        self.assertEqual(0, r)
        self.assertEqual(0, len(ps))

        # now set it up for a custom sequence
        start = datetime(2011, 1, 1)
        dur = 2.5
        self.session.monitoring.start_time = start
        self.session.allotment.period_time = dur
        self.session.monitoring.custom_sequence = "1,3,5"
        self.session.monitoring.save()

        # generate periods
        numPs = self.session.genPeriods()
        ps = self.session.period_set.all().order_by('start')

        # test
        self.assertEqual(3, numPs)
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 2, 23, 45) # 1/3
             , datetime(2011, 1, 4, 23, 45) # 1/5
              ]
        for i in range(len(ps)):
            self.assertEqual(exp[i], ps[i].start)

        # now change the sequence, and watch the periods get regenerated  
        self.session.monitoring.custom_sequence = "1,2"
        self.session.monitoring.save()

        # generate periods
        numPs = self.session.genPeriods()
        ps = self.session.period_set.all().order_by('start')

        # test
        self.assertEqual(2, numPs)
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 2)
              ]
        for i in range(len(ps)):
            self.assertEqual(exp[i], ps[i].start)

    def test_genPeriodsFromOuterLoop(self):

        # first make sure we don't crash when things
        # aren't setup
        r = self.session.genPeriodsFromOuterLoop()
        ps = self.session.period_set.all().order_by('start')
        self.assertEqual(0, r)
        self.assertEqual(0, len(ps))
        
        # setup the session
        start = datetime(2011, 1, 1)
        dur = 2.5
        day = SessionSeparation.objects.get(separation = 'day')
        week = SessionSeparation.objects.get(separation = 'week')
        self.session.monitoring.start_time = start
        self.session.allotment.period_time = dur
        self.session.allotment.allocated_repeats = 3
        self.session.interval_time = 3
        self.session.separation = day
        self.session.monitoring.outer_repeats = 3
        self.session.monitoring.outer_interval = 3
        self.session.monitoring.outer_separation = week
        self.session.allotment.save()
        self.session.monitoring.save()
        self.session.save()

        # create time sequence
        days = self.session.genDaysFromOuterLoop()
        exp = [1,3,3,21,3,3,21,3,3]
        self.assertEqual(exp, days)

        # create periods
        r = self.session.genPeriodsFromOuterLoop()
        ps = self.session.period_set.all().order_by('start')

        # test
        self.assertEqual(9, r)
        # watch out for lst drift!
        self.assertEqual(datetime(2011, 1, 1), ps[0].start) 
        self.assertEqual(datetime(2011, 1, 3, 23, 45), ps[1].start) #1/4
        self.assertEqual(datetime(2011, 3, 1, 20), ps[len(ps)-1].start) #3/2

    def test_genPeriodsFromInnerLoop(self):

        # first make sure we don't crash when things
        # aren't setup
        r = self.session.genPeriodsFromInnerLoop()
        ps = self.session.period_set.all().order_by('start')
        self.assertEqual(0, r)
        self.assertEqual(0, len(ps))
        
        # setup the session
        start = datetime(2011, 1, 1)
        dur = 2.5
        day = SessionSeparation.objects.get(separation = 'day')
        self.session.monitoring.start_time = start
        self.session.allotment.period_time = dur
        self.session.allotment.allocated_repeats = 5
        self.session.interval_time = 4
        self.session.separation = day
        self.session.allotment.save()
        self.session.monitoring.save()
        self.session.save()

        days = self.session.genDaysFromInnerLoop()
        exp = [1, 4, 4, 4, 4]
        self.assertEqual(exp, days)

        # create periods
        r = self.session.genPeriodsFromInnerLoop()
        ps = self.session.period_set.all().order_by('start')

        # test - check out the LST drift!
        self.assertEqual(5, r)
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 4,  23, 45) # 1/5
             , datetime(2011, 1, 8,  23, 30) # 1/9
             , datetime(2011, 1, 12, 23, 15) # 1/13
             , datetime(2011, 1, 16, 23, 0)  # 1/17
              ]
        for i in range(len(ps)):
            self.assertEqual(exp[i], ps[i].start)
            self.assertEqual(dur, ps[i].duration)
        
        # cleanup
        self.session.deletePeriods()

        # now change the separation to weeks
        week = SessionSeparation.objects.get(separation = 'week')
        self.session.separation = week
        self.session.save()

        days = self.session.genDaysFromInnerLoop()
        exp = [1, 28, 28, 28, 28]
        self.assertEqual(exp, days)

        # create periods
        r = self.session.genPeriodsFromInnerLoop()
        ps = self.session.period_set.all().order_by('start')

        # test - check out the big LST drift!
        self.assertEqual(5, r)
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 28, 22, 15) # 1/29
             , datetime(2011, 2, 25, 20, 15) # 2/26
             , datetime(2011, 3, 25, 18, 30) # 3/26
             , datetime(2011, 4, 22,16, 45) # 4/23
              ]
        for i in range(len(ps)):
            self.assertEqual(exp[i], ps[i].start)
            self.assertEqual(dur, ps[i].duration)

        # cleanup
        self.session.deletePeriods()

    def test_genPeriodsFromCustomSequence(self):
     
        # first make sure we don't crash when things
        # aren't setup
        r = self.session.genPeriodsFromCustomSequence()
        ps = self.session.period_set.all().order_by('start')
        self.assertEqual(0, r)
        self.assertEqual(0, len(ps))
        
        # setup the session
        start = datetime(2011, 1, 1)
        dur = 2.5
        self.session.monitoring.start_time = start
        self.session.allotment.period_time = dur
        self.session.monitoring.custom_sequence = "1,3,5"
        self.session.monitoring.save()

        # create periods
        r = self.session.genPeriodsFromCustomSequence()
        ps = self.session.period_set.all().order_by('start')

        # test
        self.assertEqual(3, r)
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 2, 23, 45) # 1/3
             , datetime(2011, 1, 4, 23, 45) # 1/5
              ]
              
        for i in range(len(ps)):
            self.assertEqual(exp[i], ps[i].start)
            self.assertEqual(dur, ps[i].duration)
        
        # cleanup
        self.session.deletePeriods()

    def test_adjustForLstDrift(self):

        dts = [datetime(2011, 1, 1)
             , datetime(2011, 1, 3)
             , datetime(2011, 1, 5)
              ]
        newDts = self.session.adjustForLstDrift(dts)
        self.assertEqual(datetime(2011, 1, 1), newDts[0])
        self.assertEqual(datetime(2011, 1, 2, 23, 45), newDts[1])
        self.assertEqual(datetime(2011, 1, 4, 23, 45), newDts[2])

        dt = datetime(2011, 1, 1)
        dts = [dt + timedelta(days = i) for i in range(60)]
        newDts = self.session.adjustForLstDrift(dts)
        # every four days we drift by another 15 minutes
        self.assertEqual(dts[0], newDts[0])
        qtr = timedelta(minutes = 15)
        self.assertEqual(dts[2], newDts[2] + qtr)
        qtr5 = timedelta(minutes = 15*5)
        self.assertEqual(dts[20], newDts[20] + qtr5)
        qtr15 = timedelta(minutes = 15*15)
        self.assertEqual(dts[57], newDts[57] + qtr15)

        dt = datetime(2011, 1, 16)
        dts = [dt + timedelta(days = i) for i in range(60)]
        newDts = self.session.adjustForLstDrift(dts)
        # every four days we drift by another 15 minutes
        self.assertEqual(dts[0], newDts[0])
        qtr = timedelta(minutes = 15)
        self.assertEqual(dts[2], newDts[2] + qtr)
        qtr5 = timedelta(minutes = 15*5)
        self.assertEqual(dts[20], newDts[20] + qtr5)
        qtr15 = timedelta(minutes = 15*15)
        self.assertEqual(dts[57], newDts[57] + qtr15)

    def test_lsts(self):
        
        ex = {'LST Include': [], 'LST Exclude': []}
        self.assertEqual(ex, self.session.get_lst_parameters())
        self.assertEqual(False, self.session.has_lst_inclusion())
        self.assertEqual(False, self.session.has_lst_exclusion())

        # now create an LST Exclusion range
        pName = "Exclude"
        lowParam = Parameter.objects.get(name="LST %s Low" % pName)
        hiParam  = Parameter.objects.get(name="LST %s Hi" % pName)

        spLow = SessionParameter(session = self.session
                               , parameter = lowParam
                               , float_value = 2.0
                                )
        spLow.save()                       
        spHi  = SessionParameter(session = self.session
                               , parameter = hiParam
                               , float_value = 4.0
                                 )
        spHi.save()                       

        # and make sure it shows up correctly
        ex = {'LST Include': [], 'LST Exclude': [(2.0, 4.0)]}
        self.assertEqual(ex, self.session.get_lst_parameters())
        self.assertEqual(False, self.session.has_lst_inclusion())
        self.assertEqual(True, self.session.has_lst_exclusion())

        include, exclude = self.session.get_lst_string()
        self.assertEqual('', include)
        self.assertEqual('2.00-4.00', exclude)

