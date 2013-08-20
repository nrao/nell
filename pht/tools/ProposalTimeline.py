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
import copy

class ProposalTimeline(object):

    def __init__(self, sponsor = None, proposal = None, timeRange = None, now = None):


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

        if now is None:
            self.now = datetime.now()
        else:
            self.now = now
        self.today = datetime(self.now.year, self.now.month, self.now.day)    

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
            ts = self.getTimesBilled(prop)
            #                       , start = self.getTimeRangeStart() 
            #                       , end = self.getTimeRangeEnd())
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

    def sliceTimeline(self, timeline, timeRange = None):
        "Given time range overlaps timeline?"

        now = self.now 
        today = self.today 
       
        if timeline is None or len(timeline) == 0:
            if timeRange is None:
               # show last week
               start = today - timedelta(days = 7)
               tl = [(start, 0.), (today, 0.)]
            else:
               tl = [(timeRange[0], 0.), (timeRange[1], 0.)]
        else:
            if timeRange is None:
                dt, t = timeline[-1]
                tl = copy.copy(timeline)
                tl.append((today, t))
            else:
                start = timeRange[0]
                end = timeRange[1]
                dtStart, tStart = timeline[0]
                dtEnd, tEnd = timeline[-1]
                # overlap?
                if end < dtStart:
                    # no overlap
                    tl = [(start, 0.), (end, 0.)]
                elif start > dtEnd:
                    # no overlap
                    tl = [(start, tEnd), (end, tEnd)]
                else:
                    # make an ordered set of the dates
                    dts = [dt for dt, t in timeline]
                    dts.extend([start, end])
                    dts = sorted(list(set(sorted(dts))))

                    # now associate the correct times with each of these
                    tmp = []
                    t = 0.0
                    for dt in dts:
                        # is there a time associated with this?
                        for date, hrs in timeline:
                            if dt == date:
                                t = hrs
                                break
                        tmp.append((dt, t))
                    # now just take the slice we want
                    tl = [(dt, t) for dt, t in tmp if dt >= start and dt <= end]
        return tl        

                        
    def extendTimeline(self, timeline, beginAt = None, upTo = None):
        "Extrapolates missing info."

        if len(timeline) < 1 or (len(timeline) < 2 and self.timeRange is None):
            return timeline

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
        if upTo is not None and upTo > dt1:
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
        #print 'tl: ', tl
        #print self.timeRange
        stl = self.sliceTimeline(tl, self.timeRange)
        #print 'stl: ', stl
        etl = self.extendTimeline(stl)
        return self.jsonDict(etl)

if __name__ == '__main__':

    wvu = DSSSponsor.objects.get(abbreviation = 'WVU')
    #pcode = 'GBT13A-037'
    pcode = 'GBT11A-025'
    prop = Proposal.objects.get(pcode = pcode)
    #prop.sponsor = wvu
    #prop.save()
    #ps = Proposal.objects.filter(semester__semester = '13A')
    #for prop in ps[5:10]:
    #    prop.sponsor = wvu
    #    prop.save()


    #pt = ProposalTimeline(proposal = pcode) #, timeRange = '12B')
    pt = ProposalTimeline(sponsor = 'WVU', timeRange = '13B')
    print pt.timeRange
    j = pt.getTimelineJsonDict()
    #pt.report()
