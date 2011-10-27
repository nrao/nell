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
from utilities.TimeAgent import adjustDateTimeTz, backoffFromMidnight
from scheduler.models    import *

class EventJson:

    """
    Provides the events in Json format needed by the project calendar.
    This class uses the template pattern to provide the JSON dictionary
    translations for certain objects.  These are then used by the
    observers' project calendar.
    It would be ideal that every *Json method had the same signature
    and returned exactly the same thing, but not quite.  Most of these
    methods take a single object, id and timezone, and return a single
    dictionary.  But others take different types of args, and some
    even return a list of dicts instead of a single one.
    """

    def getEvents(self, project, start, end, tz):
        """
        Top level function for providing all the events in json format
        the project calendar will need.
        """

        id          = 1
        jsonobjlist = []
    
        # Project blackout events
        blackouts = set([b for b in project.blackout_set.all()])
        for b in blackouts:
            jsonobjlist.extend(self.blackoutJson(b, start, end, id, tz))
            id = id + 1
    
        # NOTE: here we display ALL investigator blackouts, but
        # in the Observer Blackout section, we are only displaying blackouts
        # of observers.
        # Investigator blackout & Required Friend events
        invBlackouts = [b for i in project.investigator_set.all() \
                          for b in i.user.blackout_set.all()]
        frdBlackouts = [b for f in project.friend_set.all() \
                          for b in f.user.blackout_set.all() if f.required]
        invBlackouts.extend(frdBlackouts)
        blackouts = set(invBlackouts)
        for b in blackouts:
            jsonobjlist.extend(self.blackoutJson(b, start, end, id, tz))
            id = id + 1
    
        # Investigator reservations
        for user, reservations in project.getUpcomingReservations().items():
            for s, e in reservations:
                jsonobjlist.append(self.reservationJson(user, s, e, id))
                id = id + 1
    
        # Scheduled telescope periods
        for p in project.getPeriods():
            jsonobjlist.append(self.periodJson(p, id, tz))
            id = id + 1
    
        # Semester start dates
        date = datetime.fromtimestamp(float(start))
        for s in Semester.getFutureSemesters(date):
            jsonobjlist.append(self.semesterJson(s, id))
            id = id + 1
    
        # Scheduled telescope windows
        for w in project.get_windows():
            for wr in w.windowrange_set.all():
                jsonobjlist.append(self.windowRangeJson(wr, id))
                id = id + 1
        
        return jsonobjlist

    def mkJson(self, id, title, start, end = None, className = None):
        "Utitlity for creating json dict.  Takes datetimes."
        js = dict( id = id
                   , title = title
                   , start = start.isoformat()
                   , className = className
                   )
        # If an end datetime is specified, watch for a bug (or feature?)
        # in fullcalendar 1.5, wherein something ending at midnight
        # (ex: 2006-2-4 00:00) is displayed on that day.  The affect of 
        # this is that reservations and windows (that are just dates)
        # are being displayed for one day too many.
        if end is not None:
            js.update(dict(end = backoffFromMidnight(end).isoformat()))
        return js    

    def reservationJson(self, user, start, end, id):
        title = "%s in Green Bank." % user.name()
        return self.mkJson(id, title, start, end, 'reservation') 

    
    def blackoutJson(self, blackout, calstart, calend, id = None, tz = None):
        # TBF: we are passing in id, but NOT using it!
        calstart = datetime.fromtimestamp(float(calstart))
        calend   = datetime.fromtimestamp(float(calend))
        dates    = blackout.generateDates(calstart, calend)
        if tz is not None:
            dates = [(adjustDateTimeTz(tz, s), adjustDateTimeTz(tz, e)) for s, e in dates]
        title    = "%s: %s" % (blackout.forName() 
                             , blackout.getDescription() or "blackout")

        return [self.mkJson(blackout.id
                          , title
                          , d[0] if d[0] else None                     
                          , d[1] if d[1] else None                     
                          , 'blackout'
                           ) for d in dates]

    def periodJson(self, period, id, tz = None):
        end = period.start + timedelta(hours = period.duration)
        # TBF: use period.end(), and how come we ignore tz?
        #end = period.end()
        title = "".join(["Observing ", period.session.name])
        start = adjustDateTimeTz(tz, period.start) if tz is not None \
            else period.start
        return self.mkJson(id, title, start, end, 'period')

    def semesterJson(self, semester, id):
        title = "".join(["Start of ", semester.semester])
        return self.mkJson(id
                         , title
                         , semester.start()
                         , None
                         , 'semester')

    def windowRangeJson(self, wr, id):
        """
        This representation of the window range is meant specifically
        for the Monthly Project Calendar: that is, we use
        end_datetime here in order to get the correct number of 
        days displayed on the calendar.
        """
        title = "".join(["Window ", wr.window.session.name])
        js = self.mkJson(id
                       , title
                       , wr.start_datetime()
                       , wr.end_datetime()
                       , 'window')
        return js


