from   django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime             import *
from sesshuns.models      import *
from tools.TimeAccounting import TimeAccounting

def ljust(value, width):
    # watch out for floats
    if type(value) == type(3.14):
        return str("%5.2f" % value)[:width].ljust(width)
    else:    
        return str(value)[:width].ljust(width)

def bl(value):
    return "T" if value else "F"

def GenerateReport(start):
    outfile   = open("./DssSessionReport.txt", 'w')
    pcs       = [11, 50, 12, 10, 10]
    scs       = [3, 3, 15, 5, 9, 4, 5, 10, 8, 5, 5, 5, 5, 5, 15]
    semesters = sorted(Semester.objects.all()
                     , lambda x,y:cmp(x.semester,y.semester))
    ta        = TimeAccounting()

    for s in semesters:
        projects = sorted([p for p in s.project_set.all() if not p.complete]
                        , lambda x,y:cmp(x.pcode, y.pcode))
        if projects:
            outfile.write("\n\n")
            outfile.write("-" * 105)   
            outfile.write("\n\nTrimester: %s" %s.semester)

        for p in projects:
            outfile.write("\n\n\t%s, %s, PI: %s, Remaining/Total: %.1f/%.1f" % \
                        (p.pcode
                       , p.name[:50]
                       , p.principal_investigator().last_name if p.principal_investigator() else "None"
                       , ta.getTimeLeft(p)
                       , ta.getProjectTotalTime(p)))

            outfile.write("\n\n\t %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" %\
                   (ljust("sch",   scs[0])
                  , ljust("cmp",   scs[1])
                  , ljust("name",  scs[2])
                  , ljust("orgID", scs[3])
                  , ljust("obs type",  scs[4])
                  , ljust("type",  scs[5])
                  , ljust("freq",  scs[6])
                  , ljust("RA",    scs[7])
                  , ljust("Dec",   scs[8])
                  , ljust("tot",   scs[9])
                  , ljust("rem",   scs[10])
                  , ljust("min",   scs[11])
                  , ljust("max",   scs[12])
                  , ljust("btwn",   scs[13])
                  , ljust("rcvrs", scs[14])))

            sessions = sorted(p.sesshun_set.all()
                            , lambda x,y:cmp(x.name, y.name))
            for s in sessions:

                target = first(s.target_set.all())
                outfile.write("\n\t %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" %\
                    (ljust(bl(s.schedulable()),          scs[0])
                   , ljust(bl(s.status.complete),        scs[1])
                   , ljust(s.name,                       scs[2])
                   , ljust(s.original_id,                scs[3])
                   , ljust(s.observing_type.type,        scs[4])
                   , ljust(s.session_type.type[0],       scs[5])
                   , ljust(s.frequency,                  scs[6])
                   , ljust(target.get_horizontal(),      scs[7])
                   , ljust(target.get_vertical(),        scs[8])
                   , ljust(s.allotment.total_time,       scs[9])
                   , ljust(ta.getTimeLeft(s),            scs[10])
                   , ljust(s.min_duration,               scs[11])
                   , ljust(s.max_duration,               scs[12])
                   , ljust(s.time_between,               scs[13])
                   , ljust("".join(s.rcvrs_specified()), scs[14])
                   ))

            if p != projects[-1]:
                outfile.write("\n\t" + ("-" * 106))                 

if __name__=='__main__':
    GenerateReport(datetime.today())
