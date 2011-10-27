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
from utilities.TimeAgent import adjustDateTimeTz

class EventJson:

    """
    This class uses the template pattern to provide the JSON dictionary
    translations for certain objects.  These are then used by the
    observers' project calendar.
    It would be ideal that every *Json method had the same signature
    and returned exactly the same thing, but not quite.  Most of these
    methods take a single object, id and timezone, and return a single
    dictionary.  But others take different types of args, and some
    even return a list of dicts instead of a single one.
    """

    def reservationJson(self, user, start, end, id):
        js = { "id" : id
           , "title" : "%s in Green Bank." % user.name()
           , "start" : start.isoformat()
           , "end"   : end.isoformat()
           , "className": 'reservation'
           }
        return js   

    
    def blackoutJson(self, blackout, calstart, calend, id = None, tz = None):
        # TBF: we are passing in id, but NOT using it!
        calstart = datetime.fromtimestamp(float(calstart))
        calend   = datetime.fromtimestamp(float(calend))
        dates    = blackout.generateDates(calstart, calend)
        if tz is not None:
            dates = [(adjustDateTimeTz(tz, s), adjustDateTimeTz(tz, e)) for s, e in dates]
        title    = "%s: %s" % (blackout.forName() 
                             , blackout.getDescription() or "blackout")
        return [{
            "id"   :      blackout.id
          , "title":      title
          , "start":      d[0].isoformat() if d[0] else None
          , "end"  :      d[1].isoformat() if d[1] else None
          , "className": 'blackout'
        } for d in dates]
    

    def periodJson(self, period, id, tz = None):
        end = period.start + timedelta(hours = period.duration)
        # TBF: use:
        #end = period.end()

        return {
                "id"   : id
              , "title": "".join(["Observing ", period.session.name])
              , "start": adjustDateTimeTz(tz, period.start).isoformat() if tz is not None else period.start.isoformat()
              , "end"  : end.isoformat()
              , "className" : "period"
        }    

    def semesterJson(self, semester, id):
        return {
            "id"   :     id
          , "title":     "".join(["Start of ", semester.semester])
          , "start":     semester.start().isoformat()
          , "className": 'semester'
        }

    def windowRangeJson(self, wr, id):
        """
        This representation of the window range is meant specifically
        for the Monthly Project Calendar: that is, we use
        end_datetime here in order to get the correct number of 
        days displayed on the calendar.
        """
        return {
                "id"   :     id
              , "title":     "".join(["Window ", wr.window.session.name])
              , "start":     wr.start_datetime().isoformat()
              , "end"  :     wr.end_datetime().isoformat()
              , "className": 'window'
        }

