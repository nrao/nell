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

from datetime import datetime

class BlackoutAlerts():

    """
    This is an abstract class to handle the common methods of 
    finding issues with blackouts and various constrained sessions
    (Fixed, Elective, Windowed).
    """

    def __init__(self, quiet = True, filename = None, type = None):

        # two stages for alerts; how many days before start of object 
        # to go from stage I to stage II?
        self.stageBoundary = 15
 
        self.now = datetime.utcnow()
        
        # for reporting results
        self.quiet = quiet
        self.type = type
        defaultName = "%sAlerts.txt" % self.type
        self.filename = filename if filename is not None else defaultName
        self.reportLines = []
        
        #self.lostPeriodCount = 0
       

    def add(self, lines):
        "For use with printing reports"
        if not self.quiet:
            print lines
        self.reportLines += lines

    def write(self):        
        "For use with printing reports"
        # write it out
        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)
            f.close()

    def getBlackedOutPeriods(self, now, objs = []):
        """
        Returns the stats on future fixed sessions. For use in
        determining if alerts are raised.  Returns a list of
        offending blacked-out periods, i.e.,
        [(session, [blacked out period])]
        where the list of periods are sorted by start times.
        """
        #if len(objs) == 0:
        #    fixed = Session_Type.objects.filter(type = 'fixed')
        #    sessions = Sesshun.objects.filter(session_type = fixed)
        self.add("Retrieving periods for %d %s Sessions\n" % (len(objs), self.type))    
        injured = []
        for obj in objs: #sessions:
            self.add("Periods for (%d) %s\n" % (obj.id, obj.__str__()))
            periods = obj.getBlackedOutSchedulablePeriods(now)
            cnt = len(periods)
            self.add("%d schedulable blacked-out periods\n" % cnt)
            self.lostPeriodCount += cnt
            if periods:
                injured.append((obj, periods))
                self.add("Blacked-out periods for (%d) %s\n" % (obj.id, obj.__str__()))
                pstr = '; '.join(str(p) for p in periods)
                for p in periods:
                    self.add("%s" % pstr)
                self.add("\n")
        return injured    

    def findBlackoutAlerts(self, stage = 1, now = None, objs = []):
        """
        Finds problems with fixed sessions, and returns the proper
        response.
        Stage is determined by the earliest offending period.
        Emails will be sent to observers once per week (Monday morning)
        until 15 days before the period start date. (Stage I)
        Emails will be sent daily to all project investigators =< 15 
        days before the period end date. (Stage II)
        """

        # Just two stages (see comment above)
        assert stage in (1, 2)

        def withinBoundary(st, stage, now):
            now   = now if now is not None else datetime.utcnow()
            today = datetime(now.year, now.month, now.day)

            daysTillStart = (st - today).days
            if stage == 1:
                return daysTillStart > self.stageBoundary
            else:
                return daysTillStart <= self.stageBoundary

        return [(s, ps, stage)
                for s, ps in self.getBlackedOutPeriods(now, objs)
                    if withinBoundary(ps[0].start, stage, now)]
    
