######################################################################
#
#  Maintenance_Activity.py - defines the model classes for the
#  resource calendar.
#
#  Copyright (C) 2010 Associated Universities, Inc. Washington DC, USA.
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

from django.db                       import models
from User                            import User
from Receiver                        import Receiver
from Backend                         import Backend
from Maintenance_Telescope_Resources import Maintenance_Telescope_Resources
from Maintenance_Software_Resources  import Maintenance_Software_Resources
from Maintenance_Activity_Change     import Maintenance_Activity_Change
from Maintenance_Receivers_Swap      import Maintenance_Receivers_Swap
from datetime                        import datetime, date, time, timedelta
from nell.utilities                  import TimeAgent
from django.contrib.auth.models      import User as djangoUser
from Period                          import Period

import re

class Maintenance_Activity(models.Model):

    period             = models.ForeignKey(Period, null = True)
    telescope_resource = models.ForeignKey(Maintenance_Telescope_Resources, null = True)
    software_resource  = models.ForeignKey(Maintenance_Software_Resources, null = True)
    receivers          = models.ManyToManyField(Receiver, null = True)
    backends           = models.ManyToManyField(Backend, null = True)
    subject            = models.CharField(max_length = 200)
    start              = models.DateTimeField(null = True)
    duration           = models.FloatField(null = True, help_text = "Hours", blank = True)
    contacts           = models.TextField(null = True, blank = True)
    location           = models.TextField(null = True, blank = True)
    description        = models.TextField(null = True, blank = True)
    approved           = models.BooleanField(default = False)
    approvals          = models.ManyToManyField(Maintenance_Activity_Change,
                                                db_table = "maintenance_activity_approval",
                                                related_name = "approvals", null = True)
    modifications      = models.ManyToManyField(Maintenance_Activity_Change,
                                                db_table = "maintenance_activity_modification",
                                                related_name = "modifications", null = True)
    receiver_changes   = models.ManyToManyField(Maintenance_Receivers_Swap,
                                                db_table = "maintenance_activity_receivers_swap",
                                                null = True)
    repeat_interval    = models.IntegerField(null = True) # 0, 1, 7 for none, daily, weekly
    repeat_end         = models.DateField(null = True)    # repeat until

    class Meta:
        db_table  = "maintenance_activity"
        app_label = "sesshuns"

    def __unicode__(self):
        # these could probably all be used directly except receivers & backends
        subject       = self.subject if self.subject else 'None'
        location      = self.location if self.location else 'None'
        tel_resource  = self.telescope_resource if self.telescope_resource else 'None'
        soft_resource = self.software_resource if self.software_resource else 'None'
        receivers     = self.receivers.all() if self.id else 'None'
        backends      = self.backends.all() if self.id else 'None'
        rcvr_ch       = self.receiver_changes.all() if self.id else 'None'
        start         = self.start if self.start else 'None'
        duration      = self.duration if self.duration else 'None'
        description   = self.description if self.description else 'None'
        approved      = "Yes" if self.approved else "No"
        contacts      = self.contacts if self.contacts else 'None'
        approvals     = self.approvals.all() if self.id else 'None'
        modifications = self.modifications.all() if self.id else 'None'

        repstr = "Subject: %s\nLocation: %s\nTelescope Resource: %s\nSoftware Resource: %s\n"
        repstr += "Receivers: %s\nBackends: %s\nReceiver changes: %s\nStart: %s\n"
        repstr += "Description: %s\nApproved: %s\nApprovals: %s\n"
        repstr += "Modifications: %s\nContacts: %s\n"
        repstr %= (subject, location, tel_resource, soft_resource, receivers,
                   backends, rcvr_ch, start, description, approved, approvals,
                   modifications, contacts)

        return repstr

    def summary(self):
        """
        returns a string that looks something like this:
        Install Holography/Zpectrometer - White/Watts/Morton [T=A, S=P, R=H, B=Z]
        """
        subject = self.subject
        contacts = self.contacts
        resources = self.get_resource_summary()
        ss = "%s - %s %s" % (subject, contacts, resources)
        return ss

    def get_resource_summary(self):
        rs = "[T=%s, S=%s" % (self.telescope_resource.rc_code, self.software_resource.rc_code)

        for r in self.receivers.all():
            rs += ", R=%s" % (r.abbreviation)

        for b in self.backends.all():
            rs += ", B=%s" % (b.rc_code)

        for c in self.receiver_changes.all():
            rs += ", U=%s, D=%s" % (c.up_receiver.abbreviation, c.down_receiver.abbreviation)


        rs += "]"
        return rs

    def time_range(self):
        """
        returns a string with the time range of the activity: 08:05 -
        09:30, in ET.  TBF: will always output in ET; this is called
        from a template and a parameter indicating time-zone display
        cannot be passed in.  If the resoure calendar is to be
        displayed in UT this breaks.
        """
        start = TimeAgent.utc2est(self.start)
        delta = timedelta(hours = self.duration)
        end = start + delta
        return "%02i:%02i - %02i:%02i" % (start.time().hour, start.time().minute,
                                          end.time().hour, end.time().minute)

    def set_telescope_resource(self, resource):
        self.telescope_resource = resource

    def get_telescope_resource(self):
        return self.telescope_resource

    def set_software_resource(self, resource):
        self.software_resource = resource

    def get_software_resource(self):
        return self.software_resource

    def add_backend(self, backend):
        backend = self._get_backend(backend)

        if backend:
            self.backends.add(backend)

    def get_backends(self):
        return self.backends.all()

    def add_receiver(self, receiver):
        rcvr = self._get_receiver(receiver)

        if rcvr:
            self.receivers.add(rcvr)

    def get_receivers(self):
        return self.receivers.all()

    def set_subject(self, subject):
        self.subject = subject

    def get_subject(self):
        return self.subject

    def set_location(self, location):
        self.location = location

    def get_location(self):
        return self.location

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def add_receiver_change(self, old_receiver, new_receiver):
        rs = Maintenance_Receivers_Swap()
        rs.down_receiver = self._get_receiver(old_receiver)
        rs.up_receiver = self._get_receiver(new_receiver)
        rs.save()
        self.receiver_changes.add(rs)

    def get_receiver_changes(self):
        return self.receiver_changes.all()

    def add_approval(self, user):
        self.approved = True
        approval = Maintenance_Activity_Change()
        approval.responsible = user
        approval.date = datetime.now()
        approval.save()
        self.approvals.add(approval)

    def get_approvals(self):
        return self.approvals.all()

    def add_modification(self, user):
        self.approved = False
        change = Maintenance_Activity_Change()
        change.responsible = user
        print "user = %s" % user
        print "change.responsible = %s" % change.responsible
        change.date = datetime.now()
        print "change.date = %s" % change.date
        change.save()
        self.modifications.add(change)

    def get_modifications(self):
        return self.modifications.all()

    def check_for_conflicting_resources(self):
        """
        Checks other maintenance activities on the same day to see
        whether there are maintenance activities whose resource
        requirements conflict.  If it finds any, it appends the
        resource specification (presented in the same way the summary
        does) to a list.
        """

        start = self.start
        end = start + timedelta(days = 1)
        mas = Maintenance_Activity.objects \
              .filter(start__gte = start) \
              .filter(start__lte = end) \
              .order_by('start')

        rval = []

        for i in range(0, len(mas)):
            if self.id == mas[i].id:
                continue
            else:
                my_start = self.start
                my_end = my_start + timedelta(hours = self.duration)
                other_start = mas[i].start
                other_end = other_start + timedelta(hours = mas[i].duration)

                #check 'self' for time intersection with mas[i]
                if not (my_start >= other_end or my_end <= other_start):
                    my_summary = self.get_resource_summary()[1:-1].split(', ')
                    other_summary = mas[i].get_resource_summary()[1:-1].split(', ')

                    for i in my_summary:
                        if 'T=' in i:
                            for j in other_summary:
                                if 'T=' in j:  # both have 'T='
                                    tr = Maintenance_Telescope_Resources.objects\
                                         .filter(rc_code=i[2])[0]

                                    if j[2] not in tr.compatibility:
                                        rval.append(i)
                        elif 'S=' in i:
                            for j in other_summary:
                                if 'S=' in j:  # both have 'S='
                                    sr = Maintenance_Software_Resources.objects\
                                         .filter(rc_code=i[2])[0]

                                    if j[2] not in sr.compatibility:
                                        rval.append(i)
                        else: #everything else: receivers, backends

                            # R, U, D (for Receiver, Up and Down) are
                            # equivalent.  Flag conflicts if any of
                            # these match, i.e. U=600 matches R=600.
                            x = re.match('[RUD]=.', i)

                            for j in other_summary:
                                y = re.match('[RUD]=.', j)

                                if x and y:
                                    if i[2] == j[2]:
                                        rval.append(i)
                                elif i == j:
                                    rval.append(i)
        return rval

    def _get_receiver(self, rcvr):

        if type(rcvr).__name__ == "Receiver":
            return rcvr

        if type(rcvr) == str:
            l = Receiver.objects.filter(name = rcvr)
        elif type(rcvr) == int:
            l = Receiver.objects.filter(id = rcvr)

        if len(l):
            return l[0]
        else:
            return None

    def _get_backend(self, be):

        if type(be).__name__ == "Backend":
            return be

        if type(be) == str:
            l = Backend.objects.filter(abbreviation = be)
        elif type(be) == int:
            l = Backend.objects.filter(id = be)

        if len(l):
            return l[0]
        else:
            return None

    @staticmethod
    def get_maintenance_activity_set(period):
        """
        Returns a set of maintenance activities occuring during this
        period's duration, in time order.
        """

        # To handle repeat maintenance activity objects:
        repeatQ = (models.Q(repeat_interval = 1) | models.Q(repeat_interval = 7))\
                  & (models.Q(start__lte = period.end())  & models.Q(repeat_end__gte = period.end()))

        start_endQ = models.Q(start__gte = period.start) & models.Q(start__lte = period.end())
        periodQ = models.Q(period = period)
        mas = Maintenance_Activity.objects.filter(repeatQ | periodQ)
        r = [i for i in mas]
        r.sort(cmp = lambda x, y: cmp(x.start.time(), y.start.time()))

        # Weekly repeats have a problem: what if the repeat falls on a
        # day that is not a maintenance day?  Where should we put it?
        # One strategy is to examine the maintenance periods from 3
        # days in the past to 3 days into the future.  if none of
        # those is more suitable, we keep the weekly activity here. If
        # there is a tie, we favor the earlier date. This is done by
        # taking the modulo 7 of start - maintenance_activity.start
        # and mapping it to the values in 'dm'.  Lowest value wins.

        x = []
        dm = {4: 30, 5: 20, 6: 10, 0: 0, 1: 15, 2: 25, 3: 35}
        delta = timedelta(days = 3)
        today = TimeAgent.truncateDt(period.start)
        p = Period.get_periods_by_observing_type(today - delta, today + delta, "maintenance")

        for i in r:
            if i.repeat_interval == 7:
                start_date = TimeAgent.truncateDt(i.start)
                diff = (today - start_date).days % 7

                if (diff):
                    # doesn't fall on this date.  Is this the closest period though?

                    for j in p:
                        if j != period:  # check only other periods
                            mod = (j.start.date() - start_date.date()).days % 7

                            if dm[mod] < dm[diff]: # There is a better fit with another period
                                x.append(i)        # so don't list it here.  Mark it for deletion.
                                break

        for i in x:
            if i in r:
                r.remove(i)


        return r
