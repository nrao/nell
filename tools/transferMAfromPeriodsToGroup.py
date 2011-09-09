######################################################################
#
#  transferMAfromPeriodsToGroup.py
#
#  Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

from users.models import Maintenance_Activity, Maintenance_Activity_Group
from scheduler.models import Period
from datetime import datetime, timedelta
from nell.utilities import TimeAgent

from scheduler.models import Period

periods = Period.objects.filter(session__observing_type__type = "maintenance")\
    .exclude(state__name = "Deleted").order_by("start")

for p in periods:
    if p:
        mag = Maintenance_Activity_Group()
        mag.save()
        mag.period = p
        mag.week = TimeAgent.truncateDt(p.start - timedelta(p.start.weekday()))
        mag.deleted = True if p.state.name == 'Deleted' else False
        mag.save()
        print "Period %i -> Group %i" % (p.id, mag.id)
        mas = [m for m in p.maintenance_activity_set.all()]
        for ma in mas:
            ma.group = mag
            ma.period = None
            ma.save()

mags = Maintenance_Activity_Group.objects.all()
week = set()

for mag in mags:
    week.add(mag.week)

for w in week:
    mags = Maintenance_Activity_Group.objects.filter(week = w).order_by("period__start")
    for i in range(0, mags.count()):
        mag = mags[i]
        mag.rank = "%c" % (chr(65 + i))
        mag.save()
        print mag.rank
   
