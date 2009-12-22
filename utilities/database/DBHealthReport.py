from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *
from sets            import Set
from datetime        import date, datetime, timedelta
from tools           import TimeAccounting

def get_sessions(typ,sessions):
    return [s for s in sessions if s.session_type.type == typ]

def get_allotment_hours(sessions, typ):
    return sum([s.allotment.total_time for s in get_sessions(sessions, typ)])

def get_obs_hours(sessions, typ):
    ta = TimeAccounting()
    return sum([ta.getTime("observed", s) for s in get_sessions(session, typ)])

def missing_observer_parameter_pairs(sessions):
    pairs = [
        Set(["LST Exclude Hi", "LST Exclude Low"])
      , Set(["LST Include Hi", "LST Include Low"])
    ]

    return [s.name for s in sessions \
        if len(pairs[0].intersection(s.observing_parameter_set.all())) == 1 or \
           len(pairs[1].intersection(s.observing_parameter_set.all())) == 1]

def check_maintenance_and_rcvrs():
    "Are there rcvr changes happening w/ out maintenance days?"
    bad = []
    for dt, rcvrs in Receiver_Schedule.extract_schedule().items():
        # Well, what are the periods for this day?
        periods = Period.objects.filter(
                                   start__gt = dt.date()
                                 , start__lt = dt.date() + timedelta(days = 1)
                                 )
        # of these, is any one of them a maintenance?
        if len([p for p in periods if p.session.project.is_maintenance()]) == 0:
            bad.append(dt)
    return bad

def print_values(file, values):
    if values == []:
        file.write("\n\tNone")
    else:
        for v in values:
            file.write("\n\t%s" % v)

def GenerateReport():

    ta = TimeAccounting()

    outfile = open("./DssDbHealthReport.txt",'w')

    projects = sorted(Project.objects.all(), lambda x, y: cmp(x.pcode, y.pcode))
    sessions = sorted(Sesshun.objects.all(), lambda x, y: cmp(x.name, y.name))
    periods  = Period.objects.order_by("start")
    rcvrs    = Receiver.objects.order_by("freq_low")

    outfile.write("Projects without sessions:")
    values = [p.pcode for p in projects if p.sesshun_set.all() == []]
    print_values(outfile, values)

    outfile.write("\n\nSessions without a project:")
    values = [s.name for s in sessions if not s.project]
    print_values(outfile, values)

    outfile.write("\n\nOpen sessions with alloted time < min duration:")
    values = [s.name for s in sessions \
              if s.session_type.type == "open" and \
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

    outfile.write("\n\nSessions with negative observed time:")
    values = [(s.name, str(s.getObservedTime()), str(s.allocation.total_time)) \
        for s in sessions if ta.getTime("observed", s) < 0.0]
    print_values(outfile, values)

    outfile.write("\n\nSessions without recievers:")
    values = [s.name for s in sessions if len(s.receiver_list()) == 0]
    print_values(outfile, values)

    outfile.write("\n\nOpen sessions with default frequency 0:")
    values = [s.name for s in sessions \
              if s.session_type.type == "open" and s.frequency == 0.0]
    print_values(outfile, values)

    outfile.write("\n\nSessions with unmatched observer parameter pairs:")
    values = [s.name for s in missing_observer_parameter_pairs(sessions)]
    print_values(outfile, values)

    outfile.write("\n\nSessions with RA and Dec equal to zero:")
    values = [s.name for s in sessions \
                     for t in s.target_set.all() \
                     if t.vertical == 0.0 and t.horizontal == 0.0]
    print_values(outfile, values)

    outfile.write("\n\nSessions with frequency (GHz) out of all Rcvr bands")
    values = []
    for s in sessions:
        out_of_band = False
        # freq. must be out of band for ALL rcvrs to be reported
        rcvrs = [first(Receiver.objects.filter(abbreviation = rname)) \
            for rname in s.rcvrs_specified()]
        in_bands = [r for r in rcvrs if r.in_band(s.frequency)]
        # don't report sessions w/ out rcvrs: we do that above
        if len(in_bands) == 0 and len(rcvrs) != 0:
            values.append("%s %s %5.4f" % (s.name
                                         , s.receiver_list_simple()
                                         , s.frequency))
    print_values(outfile, values)                                         

    outfile.write("\n\nProjects without a friend:")
    values = [p.pcode for p in projects if not p.complete and not p.friend]
    print_values(outfile, values)

    outfile.write("\n\nProjects without any Schedulable sessions:")
    values = [p.pcode for p in projects \
              if not p.complete and \
              not any([s.schedulable() for s in p.sesshun_set.all()])]
    print_values(outfile, values)

    outfile.write("\n\nProjects without any observers:")
    values = [p.pcode for p in projects \
              if not p.complete and len(p.get_observers()) == 0]
    print_values(outfile, values)

    outfile.write("\n\nReceiver changes happening on days other than maintenance days:")
    values = [str(s.date()) for s in check_maintenance_and_rcvrs()]
    print_values(outfile, values)

    outfile.write("\n\nSessions for which periods are scheduled when none of their receivers are up:")
    values = [p.__str__() for p in periods if not p.has_required_receivers()]
    print_values(outfile, values)

    outfile.write("\n\nSessions with non-unique names:")
    values  = [s.name for s in sessions]
    for v in Set(values):
        values.remove(v)
    print_values(outfile, values)

    outfile.write("\n\nPeriods Scheduled on blackout dates:")
    values = []
    for s in sessions:
        for p in [p for p in s.period_set.all() if p.start >= datetime.today()]:
            blackouts = s.project.get_blackout_times(p.start, p.end())
            if blackouts:
                values.append("%s on %s" % (s.name, p.start.strftime("%m/%d/%Y %H:%M")))
    print_values(outfile, values)

    outfile.write("\n\nOverlapping periods:")
    values  = []
    overlap = []
    not_deleted_periods = [p for p in periods if p.state.abbreviation != "D"]
    for p1 in not_deleted_periods:
        start1, end1 = p1.start, p1.end()
        for p2 in not_deleted_periods:
            start2, end2 = p2.start, p2.end()
            if p1 != p2 and p1 not in overlap and p2 not in overlap:
                if overlaps((start1, end1), (start2, end2)):
                    values.append("%s and %s" % (str(p1), str(p2)))
                    overlap.extend([p1, p2])
    print_values(outfile, values)

    outfile.write("\n\nGaps in historical schedule:")
    now = datetime.utcnow()
    ps_all = Period.objects.filter(start__lt = now).order_by("start")
    ps = [p for p in ps_all if not p.isDeleted()] # TBF: use filter?
    values = []
    previous = ps[0]
    for p in ps[1:]:
        # periods should be head to tail - TBF: this catches overlaps too!
        if p.start != previous.end():
            values.append("Gap between: %s and %s" % (previous, p))
        previous = p    
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

    outfile.write("\n\nPending Periods:") 
    values  = [str(p) for p in periods if p.isPending()]
    print_values(outfile, values)

    

if __name__ == '__main__':
    GenerateReport()
