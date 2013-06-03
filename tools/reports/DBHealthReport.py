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

#!/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime                  import date, datetime, timedelta
from django.db.models          import Q

from scheduler.models          import *
from scheduler.httpadapters    import SessionHttpAdapter
from tools.database.UserInfoTools import UserInfoTools
from utilities                 import TimeAccounting
from utilities                 import AnalogSet
from tools.alerts              import SessionInActiveAlerts

def get_sessions(typ,sessions):
    return [s for s in sessions if s.session_type.type == typ]

def get_allotment_hours(sessions, typ):
    return sum([s.allotment.total_time for s in get_sessions(sessions, typ)])

def get_obs_hours(sessions, typ):
    ta = TimeAccounting()
    return sum([ta.getTime("observed", s) for s in get_sessions(session, typ)])

def invalidLSTParameters(sessions):
    "Checks for invalid LST Exclusion/Inclusion Parameters."

    def invalidLST(s):
        try:
            params  = s.get_lst_parameters()
            exclude = [(low, hi) for low, hi in params['LST Exclude']]
            include = [(low, hi) for low, hi in params['LST Include']]
        except:
            return True
        else:
            return False

    return [s.name for s in sessions if invalidLST(s)]

def repeatedObservingParameters(sessions):
    def repeatedParam(s):
        params = [op.parameter.name 
          for op in s.observing_parameter_set.filter(
            ~Q(parameter__name__contains = 'LST Exclude') & 
            ~Q(parameter__name__contains = 'LST Include'))]
        repeats = [p for p in params if params.count(p) > 1]
        return len(repeats) > 0

    return [s.name for s in sessions if repeatedParam(s)]

#def missing_observer_parameter_pairs(sessions):
#    pairs = [
#        set(["LST Exclude Hi", "LST Exclude Low"])
#      , set(["LST Include Hi", "LST Include Low"])
#    ]
#
#    return [s.name for s in sessions \
#        if len(pairs[0].intersection(s.observing_parameter_set.all())) == 1 or \
#           len(pairs[1].intersection(s.observing_parameter_set.all())) == 1]

def check_maintenance_and_rcvrs():
    "Are there rcvr changes happening w/ out maintenance days?"
    bad = []
    for dt, rcvrs in Receiver_Schedule.extract_schedule().items():
        # Well, what are the periods for this day?
        start = dt.replace(hour = 0)
        periods = Period.objects.filter(
                                   start__gt = start
                                 , start__lt = start + timedelta(days = 1)
                                 ).exclude(
                                   state__name = 'Deleted'
                                 )
        # of these, is any one of them a maintenance?
        if len([p for p in periods if p.session.project.is_maintenance()]) == 0:
            bad.append(dt.date())
    return sorted(set(bad))[1:] # Remove start of DSS

def print_values(file, values):
    if values == []:
        file.write("\n\tNone")
    else:
        for v in values:
            file.write("\n\t%s" % v)

# Windows & Blackouts:
def get_window_blackout_alerts():
    """
    If all observers have blacked out any of the time for the window default period, this will be reported in the DB Health report and handled by the scheduler/head of science ops.
    If >10% and =>50% of the opportunities possible for the window to be scheduled is blacked out by all project observers, this will be reported in the DB Health report
    If >50% of the opportunities possible for the window to be scheduled is blacked out by all project observers, this will be reported in the DB Health report
    """

    # we only care about incomplete windows
    #wins = Window.objects.filter(complete = False)
    wins = []
    alerts1 = []
    alerts2 = []
    alerts3 = []
    for w in wins:
        hrsSchd, hrsBlck, schd, bs = w.getBlackedOutSchedulableTime()
        ratio = hrsBlck/hrsSchd if hrsSchd > 0.0 else 0.0
        if ratio > .10 and ratio < .50:
            alerts1.append((w, ratio))
        elif ratio > .50:
            alerts2.append((w, ratio))
        if w.defaultPeriodBlackedOut():
            alerts3.append(w)
    return (alerts1, alerts2, alerts3)        
        

# Windowed Sessions w/ no windows (just give count)

def get_windowed_sessions_with_no_window():
    s = Sesshun.objects.all()
    sw = s.filter(session_type__type__exact = "windowed")
    windowless = [x for x in sw if len(x.window_set.all()) == 0]
    return windowless

# non-Windowed Sessions w/ windows (just give count)

def get_non_windowed_sessions_with_windows():
    s = Sesshun.objects.all()
    snw = s.exclude(session_type__type__exact = "windowed")
    windowed = [x for x in snw if len(x.window_set.all()) > 0]
    return windowed

def get_windows():
    return Window.objects.all()

# return only recent windows
def filter_current_windows(wins):
    gt_date = datetime.now().date() - timedelta(1)
    lt_date = gt_date + timedelta(62) 
    return [w for w in wins if w.start_date() is not None and w.last_date() is not None and w.start_date() < lt_date and w.last_date() > gt_date]

# Windowed Sessions that are guaranteed need default periods.
def get_missing_default_periods():
    ws = filter_current_windows(get_windows())
    return [w for w in ws if w.lacksMandatoryDefaultPeriod()]

# windows w/ out start, duration, or default_period
def get_incomplete_windows():
    ws = get_windows()
    # no periods
    win_no_period = filter_current_windows(ws.filter(default_period = None))
    # no ranges
    win_no_ranges = [w for w in ws if len(w.ranges()) == 0]
    #return (win_no_start, win_no_dur, win_no_period)
    return (win_no_ranges, win_no_period)

# windows w/ any period outside the window range
def get_win_period_outside():

    ws = Window.objects.filter(complete = False)
    wp = filter_current_windows(ws.exclude(default_period = None))
    return [w for w in wp if len(w.outOfRangePeriods()) > 0]

# overlapping windows belonging to the same session
def get_overlapping_windows():

    # we don't care about complete windows
    wins = Window.objects.filter(complete = False)
    # we also want to worry only about the present
    wins = filter_current_windows(wins)

    overlap = []
    dontcheck = []

    for w in wins:
        os = w.overlappingWindows()
        for wos in os:
            if wos.id not in dontcheck and w.id not in dontcheck:
                dontcheck.append(wos.id)
                dontcheck.append(w.id)
                overlap.append((w, wos)) 
    return overlap

# periods belonging to windowed sessions that are not assigned to a window.
def get_non_window_periods():
    ws = Sesshun.objects.filter(session_type__type__exact = "windowed")
    non_window_periods = []

    for s in ws:
        # don't care about deleted periods
        pds = s.period_set.exclude(state__name = 'Deleted')
        win = s.window_set.all()
        winp = set()

        # Set up the set of periods that belong to a window.  Doesn't
        # matter here if they're deleted or not, since we are checking
        # whether the non-deleted periods of the session are in this
        # set.  Any deleted periods in this set are harmless.
        for i in win:
            #if i.default_period:
            #    winp.add(i.default_period)

            #if i.period:
            #    winp.add(i.period)
            for p in i.periods.all():
                winp.add(p)

        for i in pds:
            if i not in winp:
                non_window_periods.append(i)

    return non_window_periods

# windows with more than one period in the scheduled state

#def get_windows_with_scheduled_periods():
#    assert False # this is legal now
#    # need a set of windows with more than one period to start with
#    ws = get_windows()
#    w = ws.exclude(default_period = None).exclude(period = None)
#    w = w.filter(period__state__name = "scheduled").filter(default_period__state__name = "scheduled")
#    return w


def get_window_out_of_range_lst():
    return [w for w in get_windows() if w.hasLstOutOfRange()]
    

# windows of the same session with less than 48 hour inter-window interval

def get_window_within_48():
    w = get_windows()
    sid = set()
    within48 = []

    for i in w:
        sid.add(i.session_id)

    for i in sid:
        wwsid = filter_current_windows(w.filter(session__id__exact = i))
        s = len(wwsid)

        # Would like to do this in terms of the model/SQL

        for j in range(0, s):
            for k in range(j + 1, s):
                w1s = wwsid[j].start_datetime()     # start datetime for window
                w1e = wwsid[j].end_datetime()       # end datetime for window
                w2s = wwsid[k].start_datetime()
                w2e = wwsid[k].end_datetime()

                # Here we check that the windows don't come closer
                # than 48 hours to each other.  To meet this
                # condition, the earlier window's end time must be
                # less at least 2 days earlier than the later window's
                # start.

                if w1s < w2s:
                    delta = w2s - w1e
#                    print w2s, "-", w1e, "=", delta
                else:
                    delta = w1s - w2e
#                    print w1s, "-", w2e, "=", delta

                if delta.days < 2:
                    within48.append((wwsid[j], wwsid[k], delta))
    return within48

# windows whose period is pending

#def get_pathological_windows():
#    pathological = []
#    w = get_windows()

#    for i in w:
#        if i.state() == None or i.dual_pending_state():
#            pathological.append(i)
#
#    return pathological


# windows with periods not represented in its session's period list

def get_windows_with_rogue_periods():
    ws = get_windows()
    w = filter_current_windows(ws.exclude(default_period = None))
    rogue = []

    for i in w:

        for p in i.periods.all():
            ps = i.session.period_set.filter(id__exact = p.id)
            if len(ps) == 0:
                rogue.append(i)

        #ps = i.session.period_set.filter(id__exact = i.default_period.id)

        #if len(ps) == 0:
        #    rogue.append(i)

        #if i.period:
        #    ps = i.session.period_set.filter(id__exact = i.period.id)

        #    if len(ps) == 0:
        #        rogue.append(i)
    return rogue

def output_windows(file, wins):
    for i in wins:
        file.write("\t%s\t%i\n" % (i.session.name, i.id))

def output_windows2(file, wins):
    for w in wins:
        file.write("%s\n" % w.__str__())

def get_closed_projets_with_open_sessions():
    p = Project.objects.filter(complete = True)
    cp = []

    for i in p:
        if i.sesshun_set.filter(status__complete = False):
           cp.append(i)

    return cp

######################################################################
# Look for sessions that have something other than just 1 target.
######################################################################

def sessions_with_null_or_multiple_targets():
    ss = Sesshun.objects.all()
    s = [x for x in ss if x.getTarget() is None]
    return s

######################################################################
# Sessions with bad targets.  A bad target is defined as a session
# that has just 1 target, but said target is missing ra and/or dec.
######################################################################

def sessions_with_bad_target():
    ss = Sesshun.objects.all()
    s = [x for x in ss if x.getTarget() is not None]
    bad_target_sessions = [x for x in s if x.target.horizontal is None
                           or x.target.vertical is None]
    return bad_target_sessions

def elective_sessions_no_electives():
    "Elective Sessions that have no electives"
    es = Sesshun.objects.filter(session_type__type = "elective")
    return [s for s in es if len(s.elective_set.all()) == 0]

def non_elective_sessions_electives():
    "Non-Elective Sessions that have electives"
    ss = Sesshun.objects.all()
    return [s for s in ss if s.session_type.type != "elective" and \
        len(s.elective_set.all()) > 0]
    
def electives_no_periods():
    "Every elective should have at least one period.  Who doesn't?"
    es = Elective.objects.all()
    return [e for e in es if len(e.periods.all()) == 0]
    
def periods_no_elective():
    "A period from an Elective Session should belong to an Elective."
    es = Sesshun.objects.filter(session_type__type = "elective")
    no_electives = []
    for s in es:
        no_electives.extend([p for p in s.period_set.all() if p.elective is None])
    return no_electives

def report_overlaps(periods, now = None):
    """
    We don't want to report on *any* overlaps in the schedule.  Apply
    some pretty complex rules to keep this more meaningful.
    """
    if now is None:
        now = datetime.utcnow()
    values  = []
    overlap = []
    not_deleted_periods = [p for p in periods if p.state.abbreviation != "D"]
    for p1 in not_deleted_periods:
        start1, end1 = p1.start, p1.end()
        for p2 in not_deleted_periods:
            start2, end2 = p2.start, p2.end()
            if p1 != p2 and p1 not in overlap and p2 not in overlap:
                # what kind of overlap?
                type = ""
                if AnalogSet.overlaps((start1, end1), (start2, end2)):
                    # in the past?
                    if p1.start < now or p2.start < now:
                        type = "Overlap in past"
                    # any scheduled?    
                    if p1.isScheduled() or p2.isScheduled():
                        type = "Overlap with scheduled period"
                    # if it's not one of the above types, see if a 3rd period
                    # is involved:
                    if type == "":
                        # check just the nearest neighbors
                        oneWeekBefore = p1.start - timedelta(days = 7)
                        oneWeekAfter  = p1.start + timedelta(days = 7)
                        neighbors = Period.objects.exclude(state__abbreviation = "D").filter(start__gt = oneWeekBefore
                                       , start__lt = oneWeekAfter)
                        for p3 in neighbors:
                            if p1 != p3 and p2 != p3 and p3 not in overlap:
                                start3, end3 = p3.start, p3.end()
                                if AnalogSet.overlaps((start1, end1), (start3, end3)) \
                                  or AnalogSet.overlaps((start2, end2), (start3, end3)):
                                    type = "Overlap of 3 periods"  
                    if type != "": 
                        values.append("%s: %s and %s" % (type, str(p1), str(p2)))
                        overlap.extend([p1, p2])
    return values


######################################################################
# Writes out the Windows reports
######################################################################

def output_windows_report(file):
    file.write("\n\nWindows:\n\n")

    w = []
    w.append(get_windowed_sessions_with_no_window())
    w.append(get_non_windowed_sessions_with_windows())
    w.append(get_incomplete_windows())
    w.append(get_win_period_outside())
    w.append(get_overlapping_windows())
    w.append(get_non_window_periods())
# 6    #w.append(get_windows_with_scheduled_periods())
    w.append(get_window_within_48())
# 8    #w.append(get_pathological_windows())
    w.append(get_windows_with_rogue_periods())
    bs1, bs2, dbs = get_window_blackout_alerts()
    w.append(bs1)
    w.append(bs2)
    w.append(dbs)
    w.append(get_window_out_of_range_lst())
    w.append(get_missing_default_periods())
    
    desc = []
    desc.append("Windowed sessions with no windows")
    desc.append("Non-windowed sessions with windows assigned")
    desc.append("Incomplete windows (missing data: ranges, period)")
    desc.append("Windows with periods whose duration extends outside window")
    desc.append("Overlapping window pairs")
    desc.append("Periods belonging in windowed sessions but not in windows")
    #desc.append("Windows with more than one period in the scheduled state")
    desc.append("Windows within same session that come within 48 hours of each other")
    #desc.append("Windows in an illegal state")
    desc.append("Windows with periods not in their session period set")
    desc.append("Windows with >10% and =<50% schedulable time blacked out")
    desc.append("Windows with >50% schedulable time blacked out")
    desc.append("Windows with default period partially blacked out")
    desc.append("Windows with LST out of range")
    desc.append("Windows from Guaranteed Sessions that lack a Default Period") 
    
    file.write("Summary\n")
    file.write("\t%s: %i\n" % (desc[0], len(w[0])))
    file.write("\t%s: %i\n" % (desc[1], len(w[1])))
    file.write("\t%s: (%i, %i)\n" % (desc[2], len(w[2][0]), len(w[2][1])))
    file.write("\t%s: %i\n" % (desc[3], len(w[3])))
    file.write("\t%s: %i\n" % (desc[4], len(w[4])))
    file.write("\t%s: %i\n" % (desc[5], len(w[5])))
    file.write("\t%s: %i\n" % (desc[6], len(w[6])))
    file.write("\t%s: %i\n" % (desc[7], len(w[7])))
    file.write("\t%s: %i\n" % (desc[8], len(w[8])))
    file.write("\t%s: %i\n" % (desc[9], len(w[9])))
    file.write("\t%s: %i\n" % (desc[10], len(w[10])))
    file.write("\t%s: %i\n" % (desc[11], len(w[11])))
    file.write("\t%s: %i\n" % (desc[12], len(w[12])))


    file.write("\n\nWindow Details\n\n")

    if len(w[0]):
        file.write("%s:\n" % (desc[0]))

        for i in w[0]:
            file.write("\t%s\n" % i.name)

    if len(w[1]):
        file.write("\n%s:\n" % (desc[1]))

        for i in w[1]:
            file.write("\t%s\n" % i.name)

    if len(w[2]):
        file.write("\n%s:\n" % (desc[2]))

        if len(w[2][0]):
            file.write("\n\tWith no range:\n")
            output_windows(file, w[2][0])

        if len(w[2][1]):
            file.write("\n\tWith no period:\n")
            output_windows(file, w[2][1])

    if len(w[3]):
        file.write("\n%s:\n" % (desc[3]))
        output_windows2(file, w[3])

    if len(w[4]):
        file.write("\n%s:\n" % (desc[4]))

        for i in w[4]:
            file.write("\t%s\t&\t%s\t\n" % \
                       (i[0].__str__(), i[1].__str__()))

    if len(w[5]):
        file.write("\n%s:\n" % (desc[5]))

        for p in w[5]:
        #    file.write("\t%s\t%i\n" % (i.session.name, i.id))
            file.write("\t%s\n" % p.__str__())

    #if len(w[6]):
    #    file.write("\n%s:\n" % (desc[6]))
    #    output_windows(file, w[6])

    #if len(w[7]):
    if len(w[6]):
        file.write("\n%s:\n\n\t(Window, Window, delta(days, seconds))\n" % (desc[6]))

        for i in w[6]:
            #exclude windows that overlap. Those are covered earlier.
            if not (i[2].days < 0 or i[2].seconds < 0):
                file.write("\t%s\t%i\t&\t%s\t%i\t(%i, %i)\n" % \
                           (i[0].session.name, i[0].id, i[1].session.name,
                            i[1].id, i[2].days, i[2].seconds))

    #if len(w[8]):
    #    file.write("\n%s:\n" % (desc[8]))
    #    output_windows(file, w[8])

    #if len(w[9]):
    if len(w[7]):
        file.write("\n%s:\n" % (desc[7]))
        output_windows2(file, w[7])

    if len(w[8]):
        file.write("\n%s:\n" % (desc[8]))
        for win, ratio in w[8]:
            file.write("%5.2f, %s\n" % (ratio, win.__str__()))
        
    if len(w[9]):
        file.write("\n%s:\n" % (desc[9]))
        for win, ratio in w[9]:
            file.write("%5.2f, %s\n" % (ratio, win.__str__()))
        
    if len(w[10]):
        file.write("\n%s:\n" % (desc[10]))
        output_windows2(file, w[10])
        
    if len(w[11]):
        file.write("\n%s:\n" % (desc[11]))
        output_windows2(file, w[11])

    if len(w[12]):
        file.write("\n%s:\n" % (desc[12]))
        output_windows2(file, w[12])

def GenerateReport():

    ta = TimeAccounting()
    ui = UserInfoTools()

    outfile = open("./DssDbHealthReport.txt",'w')

    projects = sorted(Project.objects.all(), lambda x, y: cmp(x.pcode, y.pcode))
    sessions = sorted(Sesshun.objects.all(), lambda x, y: cmp(x.name, y.name))
    periods  = Period.objects.exclude(state__name = 'Deleted').order_by('start')
    rcvrs    = Receiver.objects.order_by("freq_low")
    deleted  = Period_State.get_state('D')

    outfile.write("Projects without sessions:")
    values = [p.pcode for p in projects if len(p.sesshun_set.all()) == 0]
    print_values(outfile, values)

    outfile.write("\n\nSessions without a project:")
    values = [s.name for s in sessions if not s.project]
    print_values(outfile, values)

    outfile.write("\n\nOpen sessions (not completed) with alloted time < min duration:")
    values = [s.name for s in sessions \
              if s.session_type.type == "open" and \
                 not s.status.complete and \
                 s.allotment.total_time < s.min_duration]
    print_values(outfile, values)

    outfile.write("\n\nOpen sessions (not completed) with time left < min duration:")
    values = [s.name for s in sessions \
              if s.session_type.type == "open" and \
                 not s.status.complete and \
                 ta.getTimeLeft(s) < s.min_duration]
    print_values(outfile, values)

    outfile.write("\n\nOpen sessions with max duration < min duration:")
    values = [s.name for s in sessions \
              if s.session_type.type == "open" and \
                 s.min_duration > s.max_duration]
    print_values(outfile, values)

    outfile.write("\n\nSessions with min duration too small:")
    ss1 = [s for s in sessions if s.min_duration <= 0.25]
    ss = sorted(ss1, lambda x, y: cmp(x.min_duration, y.min_duration))
    values = ["%s, %f" % (s.name, s.min_duration) for s in ss]
    print_values(outfile, values)

    outfile.write("\n\nSessions with negative observed time:")
    values = ["%s; obs: %s, total: %s" % \
        (s.name, str(ta.getTime("observed", s)), str(s.allotment.total_time)) \
        for s in sessions if ta.getTime("observed", s) < 0.0]
    print_values(outfile, values)

    outfile.write("\n\nSessions without receivers:")
    values = [s.name for s in sessions \
              if len(s.receiver_list()) == 0 and \
                 s.project.pcode not in ("Maintenance", "Shutdown")]
    print_values(outfile, values)

    outfile.write("\n\nOpen sessions with default frequency 0:")
    values = [s.name for s in sessions \
              if s.session_type.type == "open" and s.frequency == 0.0]
    print_values(outfile, values)

    outfile.write("\n\nSessions with invalid LST Exclusion/Inclusion parameters:")
    values = invalidLSTParameters(sessions)
    print_values(outfile, values)

    outfile.write("\n\nSessions with repeated observing parameters:")
    values = repeatedObservingParameters(sessions)
    print_values(outfile, values)

    #outfile.write("\n\nSessions with unmatched observer parameter pairs:")
    #values = [s.name for s in missing_observer_parameter_pairs(sessions)]
    #print_values(outfile, values)

    outfile.write("\n\nSessions with RA and Dec equal to zero:")
    values = [s.name for s in sessions \
                     if s.getTarget() is not None and s.target.vertical == 0.0 \
                        and s.target.horizontal == 0.0]
    print_values(outfile, values)

    outfile.write("\n\nSessions with frequency (GHz) out of all Rcvr bands")
    values = []
    for s in sessions:
        out_of_band = False
        # freq. must be out of band for ALL rcvrs to be reported
        rcvrs = [Receiver.objects.get(abbreviation = rname) \
            for rname in s.rcvrs_specified()]
        in_bands = [r for r in rcvrs if r.in_band(s.frequency)]
        # don't report sessions w/ out rcvrs: we do that above
        if len(in_bands) == 0 and len(rcvrs) != 0:
            values.append("%s %s %5.4f" % (s.name
                                         , s.receiver_list_simple()
                                         , s.frequency))
    print_values(outfile, values)

    outfile.write("\n\nUpcoming Windowed, Elective, and Fixed Sessions that are not enabled:")
    sa = SessionInActiveAlerts()
    print_values(outfile
               , ["%s session %s which runs %s" % (u.session.session_type.type
                                                 , u.session.id
                                                 , sa.getRange(u))
                   for u in sa.findDisabledSessionAlerts()]
                   )

    outfile.write("\n\nUpcoming Windowed, Elective, and Fixed Sessions that are not authorized:")
    sa = SessionInActiveAlerts()
    print_values(outfile
               , ["%s session %s which runs %s" % (u.session.session_type.type
                                                 , u.session.id
                                                 , sa.getRange(u))
                   for u in sa.findUnauthorizedSessionAlerts()]
                   )

    outfile.write("\n\nProjects without a friend:")
    values = [p.pcode for p in projects if not p.complete and len(p.friend_set.all()) == 0]
    print_values(outfile, values)

    outfile.write("\n\nProjects without any schedulable sessions:")
    values = [p.pcode for p in projects \
              if not p.complete and \
              not any([s.schedulable() for s in p.sesshun_set.all()])]
    print_values(outfile, values)

    outfile.write("\n\nProjects without any observers:")
    values = [p.pcode for p in projects \
              if not p.complete and len(p.get_observers()) == 0]
    print_values(outfile, values)

    outfile.write("\n\nProjects whose project type is inconsistent with its sessions' observing types:")
    values = [p.pcode for p in projects \
                      if p.is_science() and \
                         not all([s.isScience() for s in p.sesshun_set.all()])]
    print_values(outfile, values)

    outfile.write("\n\nProjects whose category is inconsistent with its sessions' categories:")
    badCats = []
    for p in projects:
        cats = list(set([s.getCategory() for s in p.sesshun_set.all()]))
        if len(cats) > 1:
            badCats.append(p.pcode)
        elif len(cats) == 1 and cats[0] != p.get_category():
            badCats.append(p.pcode)
    print_values(outfile, badCats)
    
    outfile.write("\n\nReceiver changes happening on days other than maintenance days:")
    values = [str(s) for s in check_maintenance_and_rcvrs()]
    print_values(outfile, values)

    outfile.write("\n\nPeriods longer then 24 hours:")
    values = Period.objects.filter(duration__gt = 24.0)
    print_values(outfile, values)

    outfile.write("\n\nPeriods in the future whose receivers are different then their sessions.")
    fps = Period.objects.filter(start__gt = datetime.now()).order_by('start')
    # Here we compare what the period currently has, with the function that
    # the period was initialized with 
    bps = [p for p in fps if p.receiver_list_simple() != ", ".join(p.session.rcvrs_specified())] 
    values = ["%s at %s; %s vs. %s" % (p.session.name
                                     , p.start
                                     , p.receiver_list_simple()
                                     , ", ".join(p.session.rcvrs_specified())) \
               for p in bps]
    print_values(outfile, values)

    outfile.write("\n\nPeriods which have been observed when none of their receivers were up:")
    start = datetime(2009, 10, 10) # don't bother looking before this
    end = datetime.utcnow() - timedelta(days=1) # leave a day buffer
    obs_ps = [p for p in periods if p.start > start and p.start < end \
        and p.session.name not in ['Shutdown', 'Maintenance'] \
        and p.state != deleted]
    bad_ps = [p for p in obs_ps if not p.has_observed_rcvrs_in_schedule()]
    values = ["%s, %s" % (p.__str__(), p.receiver_list()) for p in bad_ps]
    print_values(outfile, values)

    outfile.write("\n\nSessions for which periods are scheduled when none of their receivers are up:")
    now = datetime.utcnow()
    future_ps = [p for p in periods if p.start > now \
        and p.session.project.pcode not in ['Shutdown', 'Maintenance']]
    bad_ps = [p for p in future_ps if not p.has_required_receivers()]
    values = ["%s, %s" % (p.__str__(), p.session.receiver_list_simple()) \
        for p in bad_ps]
    print_values(outfile, values)

    # note that here we use the session's rcvrs, *not* the periods'
    # rcvrs because we are looking into the future.
    outfile.write("\n\nPeriods in the future that are using retired hardware:")
    values = [p for p in periods if p.state != deleted and p.start > now and p.session.usesDeletedReceiver()] 
    print_values(outfile, values)

    outfile.write("\n\nProjects that contain non-unique session names:")
    names  = [(p.pcode, [s.name for s in p.sesshun_set.all()])
                                    for p in projects]
    values = [p for p, n in names if len(set(n)) != len(n)]
    print_values(outfile, values)

    outfile.write("\n\nUsers with duplicate accounts by name:")
    values = ui.findUsersWithSameNames()
    print_values(outfile, values)

    outfile.write("\n\nUsers with shared PST accounts:\n")
    sharedPstIds = ui.findUsersWithSamePstId(quiet = True)
    # print out useful format
    if len(sharedPstIds) > 0:
        for pst_id, us in sharedPstIds:
            outfile.write("PST ID: %s\n" % pst_id)
            for u in us:
                outfile.write("    %s, %d\n" % (u, u.id))
                outfile.write("    Projects: %s\n" % u.getProjects())
                outfile.write("    Blackouts: %s\n" % u.blackout_set.all())
    else:
        outfile.write("    None\n")

    outfile.write("\n\nUsers with no PST ID:")
    users  = list(User.objects.order_by("last_name"))
    values = [u for u in users if u.pst_id is None]
    print_values(outfile, values)

    outfile.write("\n\nPeriods Scheduled on blackout dates:")
    values = []
    for s in sessions:
        for p in [p for p in s.period_set.all() if p.start >= datetime.today() \
                                                   and not p.isDeleted()]:
            blackouts = s.project.get_blackout_times(p.start, p.end())
            if blackouts:
                values.append("%s on %s" % (s.name
                                          , p.start.strftime("%m/%d/%Y %H:%M")))
    print_values(outfile, values)

    outfile.write("\n\nElective and Fixed pending periods scheduled on blackout dates:")
    values = []
    opened = Session_Type.objects.get(type="open")
    windowed = Session_Type.objects.get(type="windowed")
    pending = Period_State.objects.get(name="Pending")
    for p in Period.objects \
                   .exclude(session__session_type=opened) \
                   .exclude(session__session_type=windowed) \
                   .filter(start__gte=now) \
                   .filter(state=pending).order_by("start"):
        blackouts = p.session.project.get_blackout_times(p.start, p.end())
        if blackouts:
            values.append("%s" % p)
    print_values(outfile, values)
        

    outfile.write("\n\nOverlapping periods:")
    values = report_overlaps(periods, now = now)
    print_values(outfile, values)


    outfile.write("\n\nGaps in historical schedule:")
    ps = Period.objects.filter(start__lt = now)\
             .filter(~Q(state__abbreviation = 'D')).order_by("start")
    values = []
    previous = ps[0]
    for p in ps[1:]:
        # periods should be head to tail 
        if p.start != previous.end() and p.start > previous.end():
            values.append("Gap between: %s and %s" % (previous, p))
        previous = p
    print_values(outfile, values)

    outfile.write("\n\nPeriods with time billed exceeding duration:")
    values  = [p.__str__() for p in periods if p.duration < p.accounting.time_billed()]
    print_values(outfile, values)

    outfile.write("\n\nPeriods with non-positive durations:")
    values  = [p for p in periods if p.duration <= 0.]
    print_values(outfile, values)

    outfile.write("\n\nPeriods with negative observed times:")
    values  = [str(p) for p in periods if p.accounting.observed() < 0.]
    print_values(outfile, values)

    outfile.write("\n\nDeleted Periods with positive observed times:")
    ps = [p for p in periods if p.state.abbreviation == 'D']
    values  = [str(p) for p in ps if p.accounting.observed() > 0.]
    print_values(outfile, values)

    outfile.write("\n\nDeleted and Scheduled Periods for non-Windowed Sessions with non-positive scheduled time:")
    ps = [p for p in periods if p.state.abbreviation in ['D', 'S'] and p.session.session_type.type != 'windowed']
    values  = [p for p in ps if p.accounting.scheduled <= 0.0]
    print_values(outfile, values)

    outfile.write("\n\nPending Periods (non-windowed, non-elective):")
    values  = [str(p) for p in periods if p.isPending() and not p.is_windowed() and not p.is_elective()]
    print_values(outfile, values)

    outfile.write("\n\nCompleted projects with non-complete sessions:")
    print_values(outfile, get_closed_projets_with_open_sessions())

    outfile.write("\n\nSessions with wrong number of targets (!= 1):")
    values = sessions_with_null_or_multiple_targets()
    print_values(outfile, values)

    outfile.write("\n\nSessions with frequency == NULL:")
    print_values(outfile, Sesshun.objects.filter(frequency = None))

    outfile.write("\n\nSessions with NULL RA and/or DEC:")
    values = sessions_with_bad_target()
    print_values(outfile, values)

    #    * (new) Incomplete electives with insufficient opportunities:
    #* Electives:
    #      o Elective sessions with no electives:
    #      o Electives with no opportunities:
    #      o Non-elective sessions with electives assigned: 

    outfile.write("\n\nElective Sessions with no Electives:")
    values = elective_sessions_no_electives()
    print_values(outfile, values)
    
    outfile.write("\n\nNon-Elective Sessions with Electives:")
    values = non_elective_sessions_electives()
    print_values(outfile, values)
    
    outfile.write("\n\nElectives with no Opportunities (Periods):")
    values = electives_no_periods()
    print_values(outfile, values)

    outfile.write("\n\nPeriods from Elective Session not in an Elective:")
    ps = periods_no_elective()
    print_values(outfile, [str(p) for p in ps])

    output_windows_report(outfile)

if __name__ == '__main__':
    GenerateReport()
