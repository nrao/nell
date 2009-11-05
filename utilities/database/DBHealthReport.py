from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *
from sets            import Set
from datetime import date,datetime,timedelta
def get_sessions(typ,sorted_sessions):
    return [s for s in sorted_sessions if s.session_type.type == typ]


def get_allotment_hours(typ,sorted_sessions):
    return sum([s.allotment.total_time for s in get_sessions(typ,sorted_sessions)])

def get_accounting_hours(typ,sorted_sessions):
    return sum([
        p.accounting.not_billable + \
        p.accounting.other_session_weather + \
        p.accounting.other_session_rfi + \
        p.accounting.other_session_other + \
        p.accounting.lost_time_weather + \
        p.accounting.lost_time_rfi + \
        p.accounting.lost_time_other - \
        p.accounting.scheduled
    for s in get_sessions(typ,sorted_sessions) for p in s.period_set.all()])

def get_hours(typ,sorted_sessions):
    return sum([get_allotment_hours(typ,sorted_sessions), get_accounting_hours(typ,sorted_sessions) ])

def missing_observer_parameter_pairs(sorted_sessions):
    ret_list=[]
    for s in sorted_sessions:
        l=[O.parameter.name for O in s.observing_parameter_set.all()]
        if ("LST Exclude Hi" in l and "LST Exclude Low" not in l) or ("LST Exclude Low" in l and "LST Exclude Hi" not in l) or ("LST Include Hi" in l and "LST Include Low" not in l) or ("LST Include Low" in l and "LST Include Hi" not in l):
            ret_list.append(s)
    return ret_list 

def overlap(start1,dur1,start2,dur2):
    end1=start1+timedelta(seconds=dur1*60*60)
    end2=start2+timedelta(seconds=dur2*60*60)
    return start1<end2 and start2<end1

def check_rcvr_period(session):
    for s in session:
        pl=[p.start.date() for p in s.period_set.all() if p.start>=datetime.today()]
        for rg in s.receiver_group_set.all():
            for r in rg.receivers.all():
                for rs in r.receiver_schedule_set.all():
                    if rs.start_date>=datetime.today() and rs.start_date.date() not in pl:
                        return True
                    else:
                        return False
 
def check_maintenance_and_rcvrs():
    "Are there rcvr changes happening w/ out maintenance days?"
    bad = []
    # cast a wide enough net to make this trimester agnostic
    start = date(2000, 1, 1)
    days = 365 * 20
    schedule = Receiver_Schedule.extract_schedule(start, days)
    changes = schedule.items()
    # the first date is a date, not a datetime, ignore it.
    for dt, rcvrs in changes[1:]:
        # is there a maintanence day this day?
        # well, what are the periods for this day?
        start_day = dt.replace(hour = 0
                             , minute = 0
                             , second = 0
                             , microsecond = 0)
        end_day = start_day + timedelta(days = 1)                     
        day_periods = Period.objects.filter(start__gt = start_day
                                          , start__lt = end_day)
        # of these, is any one of them a maintenance?
        maintenance = [p for p in day_periods \
           if p.session.project.is_maintenance()]
        if len(maintenance) == 0:
                bad.append(dt)
    return bad

def GenerateProjectReport():
    outfile = open("./dbhealthreport.txt",'w')
    outfile.write("\n Projects without sessions:")
    sorted_projects = sorted(Project.objects.all(), lambda x, y: cmp(x.pcode,y.pcode))
    sorted_sessions=sorted(Sesshun.objects.all(), lambda x,y : cmp(x.name,y.name))
    flag = False
    for p in sorted_projects:
        if len(p.sesshun_set.all())== 0:
            flag = True
            outfile.write("\n\t"+p.pcode)
    if flag==False:
        outfile.write("\n\tNone")
    flag=False
    outfile.write("\n Sessions without a project:")
    for s in [S for S in sorted_sessions if not S.project]:
        flag = True
        outfile.write("\n\t"+s.name)
    if flag==False:
        outfile.write("\n\tNone")
    flag = False
    outfile.write("\n Open sessions with time left < min duration:")
    for s in [S for S in get_sessions("open",sorted_sessions) if get_hours("open",sorted_sessions)< S.min_duration]:
        flag = True
        outfile.write("\n\t"+s.name)
    if flag==False:
        outfile.write("\n\tNone")
    flag = False
    outfile.write("\n Open sessions with max duration < min duration:")
    for s in [S for S in get_sessions("open",sorted_sessions) if S.min_duration>S.max_duration]:
        flag = True
        outfile.write("\n\t"+s.name)
    if flag==False:
        outfile.write("\n\tNone")
    flag= False
    outfile.write("\n Sessions without recievers:")
    for s in [S for S in sorted_sessions if len(S.receiver_group_set.all())== 0]:
        flag=True
        outfile.write("\n\t"+s.name)
    if flag==False:
        outfile.write("\n\tNone")
    flag=False
    outfile.write("\n Open sessions with default frequency 0:")
    for s in [S for S in get_sessions("open",sorted_sessions) if S.frequency== 0.0]:
        flag=True
        outfile.write("\n\t"+s.name)
    if flag==False:
        outfile.write("\n\tNone")
    flag = False
    outfile.write("\n Sessions with unmatched observer parameter pairs:")
    for s in missing_observer_parameter_pairs(sorted_sessions):
        flag= True
        outfile.write("\n\t"+s.name)
    if flag==False:
        outfile.write("\n\tNone")
    flag=False
    outfile.write("\n Sessions with RA and Dec equal to zero:")
    for s in [S for S in sorted_sessions for t in S.target_set.all() if t.vertical == 0.0 and  t.horizontal == 0.0]:
        flag=True
        outfile.write("\n\t"+s.name )
    if flag==False:
        outfile.write("\n\tNone")
    flag=False
    outfile.write("\n Projects without a friend:")
    for p in sorted_projects:
        if not p.complete and not p.friend:
            flag=True
            outfile.write("\n\t"+p.pcode)
    if flag==False:
        outfile.write("\n\tNone")
    flag=False
    outfile.write("\n  Projects without any Schedulable sessions:")
    for p in sorted_projects:
        if not p.complete:
            flag1 = False
            for s in p.sesshun_set.all():
                if s.schedulable():
                    flag1=True
                    break
            if flag1== False:
                flag=True
                outfile.write("\n\t"+ p.pcode)
    if flag==False:
        outfile.write("\n\tNone")
    flag=False
    outfile.write("\n  Projects without any observers:")
    for s in [p for p in sorted_projects if not p.has_sanctioned_observers() and not p.complete]:
        flag=True
        outfile.write("\n\t"+s.pcode)
    if flag==False:
        outfile.write("\n\tNone")
    flag = False
    outfile.write("\n Receiver changes happening on days other than maintenance days:")
    for s in check_maintenance_and_rcvrs():
        flag=True
        outfile.write("\n\t"+ str(s.date()))
    if flag==False:
        outfile.write("\n\t None")
    flag= False
    outfile.write("\n Sessions for which periods are scheduled when none of their receivers are up:")
    ps = Period.objects.all()
    check=[p for p in ps if not p.has_required_receivers() ]
    for p in check:
        flag=True
        outfile.write("\n\t"+p.session.name)
    if flag==False:
        outfile.write("\n\t None")
    flag=False
    outfile.write("\n Periods Scheduled on blackout dates:")
    per_blackouts=[]
    for p in sorted_projects:
        pl=[]
        for s in sorted(p.sesshun_set.all()):
            for l in [per for per in s.period_set.all() if per.start>=datetime.today()]:
                if l not in pl:
                    pl.append(l)
            for o in p.get_sanctioned_observers():
                for b in o.user.blackout_set.all():
                    for P in pl:
                        if b.start_date>=datetime.today() and overlap(P.start,P.duration,b.start_date,(b.end_date-b.start_date).seconds/(60*60)):
                            if s.name not in per_blackouts:
                                per_blackouts.append(s.name)
                                flag=True
                                outfile.write("\n\t"+s.name)#+"Period dates: start:"+str(P.start)+"  end:"+str(P.start+timedelta(seconds=P.duration*60*60))+"Blacokout: start: "+ str(b.start_date) +"  end: "+str(b.end_date))
    if flag==False:
        outfile.write("\n\t None")
    flag=False
    outfile.write("\n Overlapping periods:")
    ps=Period.objects.order_by("start")
    overlaps=[]
    for p1 in ps:
        for p2 in ps:
            if p1.id != p2.id and (p1 not in overlaps and p2 not in overlaps):
                if overlap(p1.start,p1.duration,p2.start,p2.duration):
                    flag = True
                    outfile.write("\n\t"+p1.session.name)
                    outfile.write(",\t"+p2.session.name)
                    outfile.write("\t"+str(min(p1.start,p2.start)))
                    overlaps.extend([p1,p2])
    if flag==False:
        outfile.write("\n\tNone")
    

if __name__ == '__main__':
    GenerateProjectReport()
    



