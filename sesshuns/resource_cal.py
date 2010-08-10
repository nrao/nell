######################################################################
#
#  resource_cal.py - form and views for the resource calendar specific
#  views.
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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models     import User as djangoUser
from django.http                    import HttpResponse, HttpResponseRedirect
from django.template                import Context, loader
from django.shortcuts               import render_to_response
from django                         import forms
from django.forms                   import ModelForm
from models                         import *
from pprint                         import pprint
from django.utils.safestring        import mark_safe
from django.utils.encoding          import StrAndUnicode, force_unicode
from itertools import chain
from django.utils.html              import escape, conditional_escape
from django                         import template
from nell.utilities                 import TimeAgent
from datetime                       import date, datetime, time


######################################################################
# This class is a rendering clas for the RadioSelect widget, which is
# nice enough to let us do this.  It renders the radio buttons without
# using the ugly <ul><li>rb</li></ul> construction, which puts an
# extra bullet next to the radio button, which seems a bit redundant.
# Instead, it puts a <br> after each button so that they are rendered
# neatly in a vertical orientation.
######################################################################

class BRRadioRender(forms.RadioSelect.renderer):
    """
    A class to override the standard radio button rendering.  Instead
    of using <ul><li>rb</li>...<li>rb</li></ul>, it uses
    rb<br>...rb<br>
    """

    def render(self):
        """Outputs a <br> for this set of radio fields."""
        return mark_safe(u'%s\n' % u'\n'.join([u'%s<br>'
                % force_unicode(w) for w in self]))

######################################################################
# This rendering class allows the RadioSelect widget to render the
# radio buttons horizontally.
######################################################################

class HorizRadioRender(forms.RadioSelect.renderer):
    """
    This renderer renders the radio buttons horizontally.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

######################################################################
# This class is here because the CheckboxSelectMultiple widget is not
# as nice as the RadioSelect and does not allow us to do the same
# thing with the renderers.  It doesn't have one, so we have to
# subclass the entire class to get rid of the <ul><li> bullets.
######################################################################

class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])

        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'%s %s<br>' % (rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))

######################################################################
# Load dictionary from Maintenance_Activity object
######################################################################

def load_maintenance_activity_data(ma):

    start = TimeAgent.utc2est(ma.start)
    duration = timedelta(hours = ma.duration)
    end = start + duration
    change_receiver = True if len(ma.receiver_changes.all()) else False
    old_receiver = None if not change_receiver else \
                   ma.receiver_changes.all()[0].down_receiver_id
    new_receiver = None if not change_receiver else \
                   ma.receiver_changes.all()[0].up_receiver_id

    data = {'subject'         : ma.subject,
            'date'            : start.date(),
            'time'            : start.time(),
            'end_choice'      : "end_time",
            'end_time'        : end.time(),
            'responsible'     : None if len(ma.contacts.all()) == 0 else \
                                [u.id for u in ma.contacts.all()][0],
            'location'        : ma.location,
            'telescope'       : ma.telescope_resource.id,
            'software'        : ma.software_resource.id,
            'receivers'       : [r.id for r in ma.receivers.all()],
            'change_receiver' : change_receiver,
            'old_receiver'    : old_receiver,
            'new_receiver'    : new_receiver,
            'backends'        : [b.id for b in ma.backends.all()],
            'description'     : ma.description,
            'entity_id'       : activity_id
            }

    return data

######################################################################
# The form.  All the fields for the 'Add/Edit Record' form are defined
# here.  Set the 'xxx_req' booleans appropriately to set which fields
# must be filled in by the user to be valid.
######################################################################

class RCAddActivityForm(forms.Form):

    subject_req     = True
    date_req        = True
    time_req        = True
    end_time_req    = True
    responsible_req = True
    location_req    = False
    receivers_req   = False
    backends_req    = False
    description_req = False

    subject = forms.CharField(required = subject_req, max_length=100)
    date = forms.DateField(required = date_req)
    time = forms.TimeField(required = time_req)
    end_choice = forms.ChoiceField(choices=[("end_time", "End Time"),
                                            ("duration", "Duration")],
                                   widget=forms.RadioSelect(renderer = HorizRadioRender))
    end_time = forms.TimeField(required = end_time_req)
    users = [(u.id, "%s" % (u.username))
             for u in djangoUser.objects.filter(is_staff = True).order_by('username')]
    responsible = forms.ChoiceField(required = responsible_req, choices = users)
    location = forms.CharField(required = location_req, max_length = 200)
    tel_resc = [(p.id, p.resource) for p in Maintenance_Telescope_Resources.objects.all()]
    telescope = forms.ChoiceField(choices = tel_resc,
                                  widget = forms.RadioSelect(renderer = BRRadioRender))
    soft_resc = [(p.id, p.resource) for p in Maintenance_Software_Resources.objects.all()]
    software = forms.ChoiceField(choices = soft_resc,
                                 widget = forms.RadioSelect(renderer = BRRadioRender))
    rcvr = [(p.id, p.full_description()) for p in Receiver.objects.all()]
    receivers = forms.MultipleChoiceField(required = receivers_req,
                                          choices = rcvr, widget = MyCheckboxSelectMultiple)
    rcvr.insert(0, (-1, ''))

    # This is the change receivers UI.  It consists of a checkbox and
    # two selection lists.  The selection lists are disabled if the
    # checkbox is cleared.  To do this requires some JavaScript in the
    # template.  This is provided by the function 'EnableWidget()', as
    # set below.  The function name in the attribute must match the
    # function name in the template.
    change_receiver = forms.BooleanField(
        required = False,
        widget = forms.CheckboxInput(attrs = {'onClick': 'EnableWidget()'}))
    old_receiver = forms.ChoiceField(
        label = 'down:', required = False, choices = rcvr,
        widget = forms.Select(attrs = {'disabled': 'true'}))
    new_receiver = forms.ChoiceField(
        label = 'up:', required = False, choices = rcvr,
        widget = forms.Select(attrs = {'disabled': 'true'}))

    be = [(p.id, p.full_description()) for p in Backend.objects.all()]
    backends = forms.MultipleChoiceField(required = backends_req,
                                         choices = be, widget = MyCheckboxSelectMultiple)
    description = forms.CharField(required = description_req, widget = forms.Textarea)
    entity_id = forms.IntegerField(required = False, widget = forms.HiddenInput)

######################################################################
# display_maintenance_activity(request, activity_id)
#
# Displays a summary table of the maintenance activity, with options
# to modify or delete the activity.
#
# @param request: the HttpRequest object.
# @param activity_id: the id number of the maintenance activity.
#
# @return HttpResponse.
#
######################################################################

def display_maintenance_activity(request, activity_id = None):
    if activity_id:
        ma = Maintenance_Activity.objects.filter(id = activity_id)[0]
        start = TimeAgent.utc2est(ma.start)
        duration = timedelta(hours = ma.duration)
        end = start + duration

        params = {'subject'         : ma.subject,
                  'date'            : start.date(),
                  'time'            : start.time(),
                  'end_choice'      : "end_time",
                  'end_time'        : end.time(),
                  'responsible'     : None if len(ma.contacts.all()) == 0 else \
                                      [u.username for u in ma.contacts.all()],
                  'location'        : ma.location,
                  'telescope'       : ma.telescope_resource.resource,
                  'software'        : ma.software_resource.resource,
                  'receivers'       : ", ".join([r.full_description() for r in ma.receivers.all()]),
                  'backends'        : ", ".join([b.full_description() for b in ma.backends.all()]),
                  'description'     : ma.description,
                  'activity_id'     : activity_id,
                  'approval'        : 'Yes' if ma.approved else 'No',
                  'last_modified'   : str(ma.modifications.all()[len(ma.modifications.all()) - 1]),
                  'created'         : str(ma.modifications.all()[0]),
                  'receiver_swap'   : ma.receiver_changes.all(),
                  'supervisor_mode' : True if u.username == "rcreager" else False
                 }
    else:
        params = {}

    return render_to_response('sesshuns/rc_display_activity.html',
                              params)


######################################################################
# get_maintenance_activity_group(period_id)
#
# Obtains the maintenance activity group associated with the period.
# If it doesn't exist, creates one.
######################################################################

def get_maintenance_activity_group(period_id):
    p = Period.objects.filter(id = period_id)[0]

    if len(p.maintenance_activity_group_set.all()) == 0:
        mag = Maintenance_Activity_Group(period = p)
        mag.save()

    return p.maintenance_activity_group_set.all()[0]

######################################################################
# The view.  This is called twice, by the 'GET' and 'POST' paths.  The
# period ID is needed by both the 'GET' and 'POST' paths.  It is
# provided to the 'GET' via the URL.  The 'GET' portion then stashes it
# into a hidden field, from which it can then be retrieved by the
# 'POST' portion.
######################################################################

@login_required
def add_activity(request, period_id = None):
    if request.method == 'POST':
        form = RCAddActivityForm(request.POST)

        if form.is_valid():
            # process the returned stuff here...
            print "Maintenance Period ID:", form.cleaned_data["entity_id"]
            mag = get_maintenance_activity_group(form.cleaned_data["entity_id"])
            ma = Maintenance_Activity(maintenance_group = mag)
            ma.save() # needs to have a primary key for many-to-many
                      # relationships to be set.
            process_activity(ma, form)
            return HttpResponseRedirect('/schedule/')
    else:
        if period_id:
            default_telescope = Maintenance_Telescope_Resources.objects.filter(rc_code = 'N')[0]
            default_software = Maintenance_Software_Resources.objects.filter(rc_code = 'N')[0]
            u = djangoUser.objects.filter(username = request.user)[0]
            p = Period.objects.filter(id = int(period_id))[0]
            start = TimeAgent.utc2est(p.start)

            initial_data = {'date'        : start.date(),
                            'time'        : start.time(),
                            'end_choice'  : "end_time",
                            'responsible' : u.id,
                            'telescope'   : default_telescope.id,
                            'software'    : default_software.id,
                            'entity_id'   : period_id
                            }

            form = RCAddActivityForm(initial = initial_data)
        else:
            form = RCAddActivityForm()

    return render_to_response('sesshuns/rc_add_activity_form.html', {'form': form, })


######################################################################
# The edit view.  Like the add_activity() view, this is called twice,
# by the 'GET' and 'POST' paths.  Also similar to add_activity with
# the period ID, the activity ID is needed by both the 'GET' and
# 'POST' paths.  It is provided to the 'GET' via the URL.  The 'GET'
# portion then stashes it into a hidden field, from which it can then
# be retrieved by the 'POST' portion.
######################################################################

@login_required
def edit_activity(request, activity_id = None):

    if request.method == 'POST':
        form = RCAddActivityForm(request.POST)

        if form.is_valid():
            # process the returned stuff here...
            print "Maintenance Activity ID:", form.cleaned_data["entity_id"]
            ma = Maintenance_Activity.objects.filter(id = form.cleaned_data["entity_id"])[0]
            process_activity(ma, form)
            return HttpResponseRedirect('/schedule/')
    else:
        u = djangoUser.objects.filter(username = request.user)[0]
        ma = Maintenance_Activity.objects.filter(id = activity_id)[0]

        if request.GET['ActionEvent'] == 'Modify':
            start = TimeAgent.utc2est(ma.start)
            duration = timedelta(hours = ma.duration)
            end = start + duration
            change_receiver = True if len(ma.receiver_changes.all()) else False
            old_receiver = None if not change_receiver else \
                           ma.receiver_changes.all()[0].down_receiver_id
            new_receiver = None if not change_receiver else \
                           ma.receiver_changes.all()[0].up_receiver_id

            initial_data = {'subject'         : ma.subject,
                            'date'            : start.date(),
                            'time'            : start.time(),
                            'end_choice'      : "end_time",
                            'end_time'        : end.time(),
                            'responsible'     : None if len(ma.contacts.all()) == 0 else \
                                                [u.id for u in ma.contacts.all()][0],
                            'location'        : ma.location,
                            'telescope'       : ma.telescope_resource.id,
                            'software'        : ma.software_resource.id,
                            'receivers'       : [r.id for r in ma.receivers.all()],
                            'change_receiver' : change_receiver,
                            'old_receiver'    : old_receiver,
                            'new_receiver'    : new_receiver,
                            'backends'        : [b.id for b in ma.backends.all()],
                            'description'     : ma.description,
                            'entity_id'       : activity_id
                            }

            form = RCAddActivityForm(initial = initial_data)
        elif request.GET['ActionEvent'] == 'Delete':
            ma.delete()
            return HttpResponseRedirect('/schedule/')
        elif request.GET['ActionEvent'] == 'Approve':
            ma.add_approval(u)
            ma.save()

            # Record any receiver changes in the receiver schedule table.
            for i in ma.get_receiver_changes():
                print "date =", ma.start.date()
                print "up   =", i.up_receiver
                print "down =", i.down_receiver
                rsched = datetime(ma.start.year, ma.start.month, ma.start.day, 16)
                Receiver_Schedule.change_schedule(rsched, [i.up_receiver], [i.down_receiver])

            return HttpResponseRedirect('/schedule/')
        
    return render_to_response('sesshuns/rc_add_activity_form.html', {'form': form, })

######################################################################
# def process_activity(ma, form)
#
# This is a helper function to handle the transfer of data from the
# form to the database. The only difference between the 'add_activity'
# and 'edit_activity' POST sections is in how a maintenance activity
# object is acquired.  In the first, it is created.  In the second, it
# is retrieved from the database by id.  The rest is done by this
# function.
#
# ma: The Maintenance_Activity object
# form: The RCAddActivityForm object
#
######################################################################

def process_activity(ma, form):
    """
    Does some processing in common between the add and the edit views.
    """
    # process the returned stuff here...
    ma.subject = form.cleaned_data['subject']
    print "Subject:", form.cleaned_data['subject']

    # The date and time entered into the form will be ET.  It
    # must be converted to UTC.  The end-time need not be
    # converted since a duration is computed and stored in the
    # database instead of the end time.
    start = datetime.combine(form.cleaned_data['date'], form.cleaned_data['time'])
    ma.start = TimeAgent.est2utc(start)
    print "Date:", form.cleaned_data['date']
    print "Time:", form.cleaned_data['time']

    if form.cleaned_data["end_choice"] == "end_time":
        end = datetime.combine(form.cleaned_data['date'], form.cleaned_data['end_time'])
        delta = end - start
        ma.duration = delta.seconds / 3600.0 # in decimal hours
        print "End time:", ma.duration
    else:
        duration = form.cleaned_data['end_time']
        ma.duration = duration.hour + duration.minute / 60.0 + duration.second / 3600.0
        print "Duration:", ma.duration

    u = djangoUser.objects.filter(id = form.cleaned_data["responsible"])[0]

    if len(ma.contacts.all()):
        ma.contacts.clear()
    ma.contacts.add(u)
    print "Responsible:", form.cleaned_data["responsible"]

    ma.location = form.cleaned_data["location"]
    print "Location:", form.cleaned_data["location"]

    trid = form.cleaned_data["telescope"]
    ma.telescope_resource = Maintenance_Telescope_Resources.objects.filter(id = trid)[0]
    print "Telescope:", form.cleaned_data["telescope"]

    srid = form.cleaned_data["software"]
    ma.software_resource = Maintenance_Software_Resources.objects.filter(id = srid)[0]
    print "Software:", form.cleaned_data["software"]

    ma.receivers.clear()

    for rid in form.cleaned_data["receivers"]:
        rcvr = Receiver.objects.filter(id = rid)[0]
        ma.receivers.add(rcvr)
    print "Receivers:", form.cleaned_data["receivers"]

    if form.cleaned_data["change_receiver"] == True:
        down_rcvr_id = form.cleaned_data["old_receiver"]
        up_rcvr_id = form.cleaned_data["new_receiver"]

        # What is needed is a receiver swap entry that contains our
        # receivers in the correct order (i.e. a for b, not b for a).
        # To avoid creating duplicate entries (for instance, repeated
        # swaps of a for b and b for a), search for an existing one
        # first.  If there is none, then create a new swap pair.
        mrsg = Maintenance_Receivers_Swap.objects.filter(
            down_receiver = down_rcvr_id).filter(up_receiver = up_rcvr_id)

        if len(mrsg) == 0:
            down_rcvr = Receiver.objects.filter(id = form.cleaned_data["old_receiver"])[0]
            up_rcvr = Receiver.objects.filter(id = form.cleaned_data["new_receiver"])[0]
            mrs = Maintenance_Receivers_Swap(down_receiver = down_rcvr, up_receiver = up_rcvr)
            mrs.save()
        else:
            mrs = mrsg[0]

        ma.receiver_changes.clear()
        ma.receiver_changes.add(mrs)
        print "Changing receiver %s to %s" % (form.cleaned_data["old_receiver"],
                                              form.cleaned_data["new_receiver"])
    else:
        ma.receiver_changes.clear()

    ma.backends.clear()

    for bid in form.cleaned_data["backends"]:
        be = Backend.objects.filter(id = bid)[0]
        ma.backends.add(be)
    print "Backends:", form.cleaned_data["backends"]

    ma.description = form.cleaned_data["description"]
    print "Description:", form.cleaned_data["description"]

    # Now add user and timestamp for modification.  Earliest mod is
    # considered creation.
    ma.add_modification(u)
    ma.save()
