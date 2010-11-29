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
from Maintenance_Other_Resources     import Maintenance_Other_Resources
from Maintenance_Activity_Change     import Maintenance_Activity_Change
from Maintenance_Receivers_Swap      import Maintenance_Receivers_Swap
from datetime                        import datetime, date, time, timedelta
from nell.utilities                  import TimeAgent
from django.contrib.auth.models      import User as djangoUser
from Period                          import Period

import re # regular expressions

class Maintenance_Activity(models.Model):

    period             = models.ForeignKey(Period, null = True)
    telescope_resource = models.ForeignKey(Maintenance_Telescope_Resources,
                                           null = True)
    software_resource  = models.ForeignKey(Maintenance_Software_Resources,
                                           null = True)
    other_resources    = models.ManyToManyField(Maintenance_Other_Resources,
                                                db_table = "maintenance_other_resources_map",
                                                null = True)
    receivers          = models.ManyToManyField(Receiver, null = True)
    backends           = models.ManyToManyField(Backend, null = True)
    subject            = models.CharField(max_length = 200)
    _start             = models.DateTimeField(null = True)
    duration           = models.FloatField(null = True, help_text = "Hours",
                                           blank = True)
    contacts           = models.TextField(null = True, blank = True)
    location           = models.TextField(null = True, blank = True)
    description        = models.TextField(null = True, blank = True)
    approved           = models.BooleanField(default = False)
    approvals          = models.ManyToManyField(
        Maintenance_Activity_Change,
        db_table = "maintenance_activity_approval",
        related_name = "approvals", null = True)
    modifications      = models.ManyToManyField(
        Maintenance_Activity_Change,
        db_table = "maintenance_activity_modification",
        related_name = "modifications", null = True)
    receiver_changes   = models.ManyToManyField(
        Maintenance_Receivers_Swap,
        db_table = "maintenance_activity_receivers_swap",
        null = True)
    deleted            = models.BooleanField(default = False)

    # The following enable the repeat feature.  Repeat
    # Maintenance_Activity (MA) objects are distinct objects, based on
    # an original and subsequent modifying templates.  Thus an entire
    # sequence of repeats may be deleted/modified, or just one, or all
    # future ones, etc.  Repeat MAs will point to the original
    # template via the 'repeat_template' FK.  Modifications downstream
    # will be accounted for by the 'future_template' FK on the
    # original and subsequent templates, which will point to a newer
    # definition of the MA.
    repeat_template    = models.ForeignKey(
        'self', null = True, related_name = 'repeat_template_instance')
    future_template    = models.ForeignKey(
        'self', null = True, related_name = 'future_template_instance')
    # recurrence interval: 0, 1, 7, 30 for none, daily, weekly, monthly
    repeat_interval    = models.IntegerField(null = True)
    # recurrence until this date.
    repeat_end         = models.DateField(null = True)


    class Meta:
        db_table  = "maintenance_activity"
        app_label = "sesshuns"

    def __unicode__(self):
        # these could probably all be used directly except receivers & backends
        subject       = self.subject if self.subject else 'None'
        location      = self.location if self.location else 'None'
        tel_resource  = self.telescope_resource \
            if self.telescope_resource else 'None'
        soft_resource = self.software_resource \
            if self.software_resource else 'None'
        receivers     = self.receivers.all() if self.id else 'None'
        backends      = self.backends.all() if self.id else 'None'
        rcvr_ch       = self.receiver_changes.all() if self.id else 'None'
        start         = self.get_start() if self._start else 'None'
        duration      = self.duration if self.duration else 'None'
        description   = self.description if self.description else 'None'
        approved      = "Yes" if self.approved else "No"
        contacts      = self.contacts if self.contacts else 'None'
        approvals     = self.approvals.all() if self.id else 'None'
        modifications = self.modifications.all() if self.id else 'None'

        interval_names = {0:"None", 1:"Daily", 7:"Weekly", 30:"Monthly"}

        if self.is_repeat_activity():
            repeat = "Yes"
            repeat_template = self.repeat_template.id
            repeat_interval = interval_names[self.repeat_template.repeat_interval]
            repeat_end = self.repeat_template.repeat_end
        elif self.is_repeat_template():
            repeat = "Template"
            repeat_template = self.id
            repeat_interval = interval_names[self.repeat_interval]
            repeat_end = self.repeat_end
        else:
            repeat = "No"
            repeat_template = "None"
            repeat_interval = interval_names[self.repeat_interval]
            repeat_end = self.repeat_end

        repstr = ("Subject: %s\nLocation: %s\nTelescope Resource: %s\n"
                  "Software Resource: %s\nReceivers: %s\nBackends: %s\n"
                  "Receiver changes: %s\nStart: %s\n"
                  "Description: %s\nApproved: %s\nApprovals: %s\n"
                  "Modifications: %s\nContacts: %s\n"
                  "Repeat: %s\nRepeat template: %s\nRepeat interval: %s\n"
                  "Repeat end: %s\n") % \
                  (subject, location, tel_resource, soft_resource, receivers,
                   backends, rcvr_ch, start, description, approved, approvals,
                   modifications, contacts, repeat, repeat_template,
                   repeat_interval, repeat_end)

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
        rs = "[T=%s, S=%s" % (self.telescope_resource.rc_code,
                                    self.software_resource.rc_code)

        for r in self.receivers.all():
            rs += ", R=%s" % (r.abbreviation)

        for b in self.backends.all():
            rs += ", B=%s" % (b.rc_code)

        for c in self.receiver_changes.all():
            rs += ", U=%s, D=%s" % (c.up_receiver.abbreviation, c.down_receiver.abbreviation)

        for o in self.other_resources.all():
            rs += ", O=%s" % (o.rc_code)

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
        start = self.get_start('EST')
        delta = timedelta(hours = self.duration)
        end = start + delta
        return "%02i:%02i - %02i:%02i" % (start.time().hour, start.time().minute,
                                          end.time().hour, end.time().minute)

    def get_start(self, tzname = None):
        if self.period:
            start = datetime(self.period.start.year, self.period.start.month,
                             self.period.start.day,
                             self._start.hour, self._start.minute)
        else:
            start = self._start

        return TimeAgent.utc2est(start) if tzname == 'EST' else start

    def set_start(self, start, tzname = None):
        if tzname == 'EST':
            self._start = TimeAgent.est2utc(start)
        else:
            self._start = start

    def get_end(self, tzname = None):
        d = timedelta(hours = self.duration)
        return self.get_start(tzname) + d

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
        change.date = datetime.now()
        change.save()
        self.modifications.add(change)

    def get_modifications(self):
        return self.modifications.all()

    def is_repeat_activity(self):
        return True if self.repeat_template else False

    def is_repeat_template(self):
        return False if int(self.repeat_interval) == 0 else True

    def is_future_template(self):
        if self.repeat_template and self.repeat_template.future_template:
            return self.repeat_template.future_template == self

        return False

    def get_template(self, period):
        """
        Walks up the chain of a repeat activity, starting with the
        template (self).  If the template has a pointer to a more
        recent template (i.e. the activity was modified for all future
        activities), it will go to that one.  It will stop when there
        are no more activities acting as templates, or if the
        remaining templates start after the given period.
        """

        rval = self
        mat  = self.future_template

        while mat:
            if period.start > mat.get_start():
                rval = mat
                mat = mat.future_template
            else:
                break

        return rval

    def set_as_new_template(self):
        mat = self.repeat_template
        mat.future_template = self
        mat.save()
        self.save()


    ######################################################################
    # Copies the basic event data from the provided activity to this
    # one.
    ######################################################################

    def copy_data(self, ma):
        self.telescope_resource = ma.telescope_resource
        self.software_resource  = ma.software_resource
        self.subject            = ma.subject
        self.duration           = ma.duration
        self.contacts           = ma.contacts
        self.location           = ma.location
        self.description        = ma.description

        for j in ma.receivers.all():
            self.receivers.add(j)

        for j in ma.backends.all():
            self.backends.add(j)

        for j in ma.receiver_changes.all():
            self.receiver_changes.add(j)

        for j in ma.other_resources.all():
            self.other_resources.add(j)

    ######################################################################
    # Makes a deep copy of the model instance, creating a new object
    # in the database.  Since Django does not provide a method to do
    # such a thing it is attempted here, by making a deep copy of the
    # orignial object.  Fields that are many-to-many need to be copied
    # over by looping over the source field's 'all()' list and adding
    # the items one by one to the destination object's field by using
    # the 'add()' method for that field. Not every field will be
    # identical: the 'id' field of the copy will be unique, and if
    # this is a copy of a repeated maintenance activity template the
    # repeat fields will not be the same.
    #
    # It also makes no sense to copy the approval or modification
    # history, since this will be a new maintenance activity.
    ######################################################################

    def clone(self, period = None):
        """
        Creates a clone of the template, assigning the 'period' field
        to the parameter 'period' if this parameter is provided.  The
        object will not be identical: there will be a different id,
        for instance.
        """

        ma = Maintenance_Activity();
        ma.save()
        # will be overwritten if template and period provided.
        ma.period = self.period
        # subject to a more recent one being found (see below)
        template = self

        # If this is a repeat template:
        if self.repeat_interval:
            ma.repeat_interval = 0
            ma.repeat_end = None
            ma.repeat_template = self.repeat_template \
                if self.repeat_template else self

            if period:
                ma.period = period
                template = self.get_template(period)

                # all maintenance activities are based on local time,
                # i.e. start 8:00 AM means that regardless of whether
                # DST is active or not.  To do this, we get ET version
                # of period and template start so that it can be saved
                # as the appropriate UTC time to account for DST.
                t_start = template.get_start('EST')
                p_start = TimeAgent.utc2est(period.start)

                start = datetime(p_start.year, p_start.month, p_start.day,
                                 t_start.hour, t_start.minute)

            # if this is a template, include the original creation
            # date for the repeat activity.
            ma.modifications.add(template.modifications.all()[0])

        ma.copy_data(template)
        ma.set_start(start if start else template.start, 'EST' if start else None)
        ma.save()
        return ma

    # To check for conflicts, a maintenance activity needs to check
    # itself against any other maintenance activity that day.  This is
    # the problem: Some maintenance activities are tied to periods,
    # and their times are therefore tied to that period in software,
    # but not in the database.  Further, there are repeating
    # maintenance activities. TBF.

    def check_for_conflicting_resources(self, mas):
        """
        Checks other maintenance activities on the same day to see
        whether there are maintenance activities whose resource
        requirements conflict.  If it finds any, it appends the
        resource specification (presented in the same way the summary
        does) to a list.
        """

        start = TimeAgent.truncateDt(self.get_start())
        end = start + timedelta(days = 1)
        rval = []

        for i in range(0, len(mas)):
            if self.id == mas[i].id:
                continue

            else:
                my_start = self.get_start()
                my_end = my_start + timedelta(hours = self.duration)
                other_start = mas[i].get_start()
                other_end = other_start + timedelta(hours = mas[i].duration)

                #check 'self' for time intersection with mas[i]
                if not (my_start >= other_end or my_end <= other_start):
                    my_summary = self.get_resource_summary()[1:-1].split(', ')
                    other_summary = mas[i].get_resource_summary()[1:-1]\
                        .split(', ')

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
                                        print "i =", i, "\tj =", j
                                        rval.append(i)
                        elif 'O=' in i:
                            #get resource 'x' in 'O=x'
                            other = Maintenance_Other_Resources.objects\
                                    .filter(rc_code=i[2])[0]

                            for j in other_summary:
                                # 'None' does not conflict with anything
                                if 'N' not in i:
                                    if 'O=' in j \
                                            and j[2] not in other.compatibility:
                                        rval.append(i)

                                    if 'R=' in j \
                                            and 'R' not in other.compatibility:
                                        rval.append(i)

                                    if 'B=' in j \
                                            and 'B' not in other.compatibility:
                                        rval.append(i)

                        else: #everything else: receivers, backends

                            # R, U, D (for Receiver, Up and Down) are
                            # equivalent.  Flag conflicts if any of
                            # these match, i.e. U=600 matches R=600.
                            # Also check against 'O=' not N

                            x = re.match('[RUD]=.', i)

                            for j in other_summary:
                                y = re.match('[RUD]=.', j)

                                if x and y:
                                    if i[2:] == j[2:]:
                                        rval.append(i)
                                elif i == j:
                                    if not 'T=' in i \
                                            and not 'S=' in i and not 'O=' in i:
                                        rval.append(i)

                                elif 'O=' in j and 'N' not in j:
                                    #get resource 'x' in 'O=x'
                                    other = Maintenance_Other_Resources.objects\
                                            .filter(rc_code=j[2])[0]

                                    if i[0] not in other.compatibility:
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
        repeatQ = models.Q(deleted = False) \
            & (models.Q(repeat_interval = 1) \
                   | models.Q(repeat_interval = 7) \
                   | models.Q(repeat_interval = 30)) \
                   & (models.Q(_start__lte = period.end()) \
                          & models.Q(repeat_end__gte = period.end()))

        start_endQ = models.Q(start__gte = period.start) \
            & models.Q(start__lte = period.end())

        periodQ = models.Q(period = period)
        dbmas   = Maintenance_Activity.objects.filter(periodQ)
        dbrmas  = Maintenance_Activity.objects.filter(repeatQ)
        mas     = [i for i in dbmas if not i.is_repeat_template()]
        rmas    = [i for i in dbrmas]

        # rmas is the list repeating activity templates that may apply
        # for this period.  We need clones of these to include in mas.
        # If however there are already clones in mas, we'll want to
        # skip that template.

        x = []

        for i in rmas:
            for j in mas:
                if j.repeat_template == i:
                    x.append(i)

        # Weekly repeats have a problem: what if the repeat falls on a
        # day that is not a maintenance day?  Where should we put it?
        # One strategy is to examine the maintenance periods from 3
        # days in the past to 3 days into the future.  if none of
        # those is more suitable, we keep the weekly activity here. If
        # there is a tie, we favor the earlier date. This is done by
        # taking the modulo 7 of start - maintenance_activity.start
        # and mapping it to the values in 'dm'.  Lowest value wins.

        dm = {4: 30, 5: 20, 6: 10, 0: 0, 1: 15, 2: 25, 3: 35}
        delta = timedelta(days = 3)
        today = TimeAgent.truncateDt(period.start)
        p = Period.get_periods_by_observing_type(today - delta,
                                                 today + delta,
                                                 "maintenance")

        for i in rmas:
            if i.repeat_interval > 1:
                start_date = TimeAgent.truncateDt(i.get_start())
                diff = (today - start_date).days % i.repeat_interval

                if diff:
                    # doesn't fall on this date.  Is this the closest
                    # period though?

                    if diff > 6:     # monthly not due
                        x.append(i)
                    else:            # weekly or monthly that is due this week
                        for j in p:
                            if j != period:  # check only other periods
                                mod = (j.start.date() \
                                           - start_date.date()).days \
                                           % i.repeat_interval

                                # Test to see if it's a better fit in
                                # another period.  and if so, don't
                                # use here.
                                if mod < 7 and dm[mod] < dm[diff]:
                                    x.append(i)
                                    break

        # Now that we have a list of templates that are not suitable,
        # cull the template list:
        for i in x:
            if i in rmas:
                rmas.remove(i)

        # The remaining templates may be used:
        for i in rmas:
            ma = i.clone(period)
            mas.append(ma)

        # remove all activities marked deleted.  This must be done
        # after all the above to prevent a replacement being generated
        # for a deleted activity.
        mas = [i for i in mas if not i.deleted]
        mas.sort(cmp = lambda x, y: cmp(x.get_start().time(),
                                        y.get_start().time()))

        return mas

    @staticmethod
    def list_templates():
        for i in Maintenance_Activity.objects.all():
            if i.is_repeat_template():
                ft = i

                while ft:
                    print ft.id,

                    if ft.future_template:
                        print "-->",

                    if ft.deleted:
                        print "(D)",

                    ft = ft.future_template

                print



    @staticmethod
    def list_repeat_activities():
        for i in Maintenance_Activity.objects.all():
            if i.is_repeat_activity():
                print "%s\t%s\t%s" % (i.get_start('EST'),
                                      i.id,
                                      i.repeat_template.id),

                if i.deleted:
                    print "\t(D)",

                print
