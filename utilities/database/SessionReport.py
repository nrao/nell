from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *
from tools.TimeAccounting import TimeAccounting
from sets                 import Set
from datetime             import *

# TBF: isn't this the same as TimeAccounting.getProjSessionsTotalTime
def get_total_time(project):
    return sum([s.allotment.total_time for s in project.sesshun_set.all()])

def get_remaining_time(project,ta):
    #ta = TimeAccounting()
    return sum([ta.getTimeLeft(s) for s in project.sesshun_set.all()])

def ljust(value, width):
    # watch out for floats
    if type(value) == type(3.14):
        return str("%5.2f" % value)[:width].ljust(width)
    else:    
        return str(value)[:width].ljust(width)

def get_ra(sess):
    tg = sess.target_set.all()[0]
    return tg.vertical

def get_dec(sess):
    tg = sess.target_set.all()[0]
    return tg.horizontal

def GenerateReport(start):
    outfile = open("./DssSessionReport.txt", 'w')
    sorted_semesters=sorted(Semester.objects.all(),lambda x,y:cmp(x.semester,y.semester))
    ta = TimeAccounting()
    pcs = [11, 50, 12, 10, 10]
    scs = [11, 15, 13, 12, 9, 5, 5, 10, 10, 5, 5, 7, 15]
    for s in sorted_semesters:
        outfile.write("\n\n Trimester : %s" %s.semester)
        outfile.write("\n-----------------")
        the_projects=[p for p in s.project_set.all() if not p.complete]
        projects = sorted(the_projects, lambda x,y:cmp(x.pcode, y.pcode))
        if projects:
            outfile.write("\n\n \t%s \t %s \t %s \t %s \t %s" % \
                (str("pcode").ljust(pcs[0])
               , str("name").ljust(pcs[1])
               , str("PI").ljust(pcs[2])
               , str("total hrs").ljust(pcs[3])
               , str("remaining").ljust(pcs[4])))
            outfile.write("\n\t" + ("-"*115))   
            for p in projects:
                outfile.write("\n\n \t%s \t %s \t %s \t %s \t %s" % \
                            (p.pcode.ljust(pcs[0])
                           , p.name[:50].ljust(pcs[1])
                           , p.principal_investigator().last_name.ljust(pcs[2])
                           , str(get_total_time(p)).ljust(pcs[3])
                           , str(get_remaining_time(p,ta)).ljust(pcs[4])
                            ))
                outfile.write("\n\n\t\t %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %\
                       (ljust("scheduable",     scs[0])
                      , ljust("name",           scs[1])
                      , ljust("obs type",       scs[2])
                      , ljust("session type",   scs[3])
                      , ljust("frequency",      scs[4])
                      , ljust("RA",             scs[5])
                      , ljust("Dec",            scs[6])
                      , ljust("total hrs",      scs[7])
                      , ljust("remaining",      scs[8])
                      , ljust("min",            scs[9])
                      , ljust("max",            scs[10])
                      , ljust("between",        scs[11])
                      , ljust("rcvrs",          scs[12])
                      ))
                outfile.write("\n\t\t" + ("-"*140))                 
                sess = sorted(p.sesshun_set.all(), \
                           lambda x,y:cmp(x.name, y.name))
                for s in sess: #p.sesshun_set.all():

                    outfile.write("\n\t\t %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %\
                        (ljust(s.schedulable(),        scs[0])
                       , ljust(s.name,                 scs[1])
                       , ljust(s.observing_type.type,  scs[2])
                       , ljust(s.session_type.type,    scs[3])
                       , ljust(s.frequency,            scs[4])
                       , ljust(get_ra(s),              scs[5])
                       , ljust(get_dec(s),             scs[6])
                       , ljust(s.allotment.total_time, scs[7])
                       , ljust(ta.getTimeLeft(s),      scs[8])
                       , ljust(s.min_duration,         scs[9])
                       , ljust(s.max_duration,         scs[10])
                       , ljust(s.time_between,         scs[11])
                       , ljust("".join(s.rcvrs_specified()), scs[12])
                       )
                     )
                    
        else:
            outfile.write("\n\t None")

if __name__=='__main__':
    start = datetime.today()
    GenerateReport(start)

