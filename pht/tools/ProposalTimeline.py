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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from pht.models    import *
from pht.utilities import *

from scheduler.models import Period as DSSPeriod
from scheduler.models import Sponsor as DSSSponsor
from scheduler.models import Semester as DSSSemester

from datetime import datetime, timedelta

class ProposalTimeline(object):

    def __init__(self, sponsor = None, proposal = None, timeRange = None):

        if sponsor is not None and proposal is not None:
            raise "Mutually Exclusive options: sponsor and proposal"

        if sponsor is not None:
            self.sponsor = DSSSponsor.objects.get(abbreviation = sponsor)
            
        if proposal is not None:
            self.proposals = [Proposal.objects.get(pcode = proposal)]
        else: # sponsors!
            self.proposals = Proposal.objects.exclude(sponsor = None)

        if timeRange is not None:
            sem = DSSSemester.objects.get(semester = timeRange)
            self.timeRange = (sem.start(), sem.end())
        else:
            self.timeRange = None

    def inDtRange(self, dt, start, end):
        return dt > start and dt <= end

    def getTimeRangeStart(self):
        return self.timeRange[0] if self.timeRange is not None else None

    def getTimeRangeEnd(self):
        return self.timeRange[1] if self.timeRange is not None else None

    def getProposalsAllocatedTime(self):
        return sum([p.allocatedTime() for p in self.proposals])

    def getTimeline(self):
        """
        Returns a list of tuples giving each day that the time billed has
        changed for all the proposals of interest.
        """

        now = datetime.now()
        start = now

        # for each proposal, get the periods and how much each was billed
        times = []
        for prop in self.proposals:
            ts = self.getTimesBilled(prop
                                   , start = self.getTimeRangeStart() 
                                   , end = self.getTimeRangeEnd())
            if len(ts) > 0:
                times.extend(ts)
                # keep track of what the earliest date is
                first, t = ts[0]
                if first < start:
                    start = first

        # now, take all those times and bin them by day
        firstDay = datetime(start.year, start.month, start.day)
        today = datetime(now.year, now.month, now.day)
        tomorrow = today + timedelta(days = 1)

        totalTime = 0.
        steps = []
        # step size == 1 day
        start = firstDay
        end = start + timedelta(days = 1)
        for day in range((tomorrow - firstDay).days):
            # any periods fall in this range?
            timeInStep = sum([hrs for dt, hrs in times if self.inDtRange(dt, start, end)])
            if timeInStep != 0.0:
                totalTime += timeInStep
                steps.append((firstDay + timedelta(days = day)
                            , totalTime))
            # get ready for next loop
            start = end 
            end += timedelta(days = 1)

        return steps

    def getTimesBilled(self, prop, start = None, end = None):
        "Returns the start time and time billed for all periods"
        if prop.dss_project is None:
            return []
        if start is None:
            # start from the beginning of time
            start = datetime(1971, 1, 22)
        if end is None:    
            # no point going past today
            end = datetime.now()
        ps = DSSPeriod.objects.filter(session__project__pcode = prop.dss_project.pcode
                                    , start__gt = start
                                    , start__lt = end).order_by('start')
        return [(p.start, p.accounting.time_billed()) for p in ps]

    def extendTimeline(self, timeline):
        "Extrapolates missing info."

     
        if len(timeline) < 1 or (len(timeline) < 2 and self.timeRange is None):
            return timeline

        beginAt = self.getTimeRangeStart()
        upTo    = self.getTimeRangeEnd()

        if upTo is None:
            now = datetime.now()
            upTo = datetime(year = now.year, month = now.month, day = now.day)

        start, t0 = timeline[0]

        extendedTl = []

        # do we need to add stuff to the beginning?
        if beginAt is not None and beginAt < start:
            days = (start - beginAt).days
            extendedTl.extend([(beginAt + timedelta(days = d), 0) for d in range(0, days)])
            
        extendedTl.append((start, t0))
        for i in range(len(timeline)-1):
            dt0, t0 = timeline[i]
            dt1, t1 = timeline[i+1]
            days = (dt1 - dt0).days
            # here we extrapolate for the days between
            extendedTl.extend([(dt0 + timedelta(days = d), t0) for d in range(1, days)])
            extendedTl.append((dt1, t1))

        # finish extending from the end to 'up to'    
        if upTo > dt1:
            days = (upTo - dt1).days
            extendedTl.extend([(dt1 + timedelta(days = d), t1) for d in range(1, days)])

        return extendedTl    

    def jsonDict(self, timeline):
        "Converts list of (dt, hrs) to dict ready for json (should be in views.py really?)"
        allocated = self.getProposalsAllocatedTime()
        return [dict(date = datetime.strftime(dt, "%Y/%m/%d")
                   , hrs = hrs
                   , allocated = allocated) for dt, hrs in timeline]

    def getTimelineJsonDict(self):
        "Computes Timeline and returns it in proper format"
        tl = self.getTimeline()
        etl = self.extendTimeline(tl)
        return self.jsonDict(etl)

    def report(self):

        tl = self.getTimeline()
        print tl
        etl = self.extendTimeline(tl)
        #print etl
        #print len(etl)
        return etl

if __name__ == '__main__':

    wvu = DSSSponsor.objects.get(abbreviation = 'WVU')
    pcode = 'GBT13A-037'
    prop = Proposal.objects.get(pcode = pcode)
    prop.sponsor = wvu
    prop.save()
    #ps = Proposal.objects.filter(semester__semester = '13A')
    #for prop in ps[5:10]:
    #    prop.sponsor = wvu
    #    prop.save()


    #pt = ProposalTimeline(proposal = pcode, timeRange = '12B')
    pt = ProposalTimeline(sponsor = 'WVU', timeRange = '13A')
    print pt.timeRange
    pt.report()
