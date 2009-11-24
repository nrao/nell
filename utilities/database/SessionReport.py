from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *
from tools.TimeAccounting import TimeAccounting
from sets                 import Set
from datetime             import *

def get_total_time(project):
    return sum([s.allotment.total_time for s in project.sesshun_set.all()])

def get_remaining_time(project,ta):
    #ta = TimeAccounting()
    return sum([ta.getTimeLeft(s) for s in project.sesshun_set.all()])

def GenerateReport(start):
    outfile = open("./DssSessionReport.txt", 'w')
    sorted_semesters=sorted(Semester.objects.all(),lambda x,y:cmp(x.semester,y.semester))
    ta = TimeAccounting()
    for s in sorted_semesters:
        outfile.write("\n\n Trimester : %s" %s.semester)
        outfile.write("\n-----------------")
        projects=[p for p in s.project_set.all() if not p.complete]
        if projects:
            for p in projects:
                outfile.write("\n\n \t%s \t %s \t %s \t %s \t %s" % \
                                (p.pcode.ljust(11)
                              , p.name
                              , p.principal_investigator()
                              , str(get_total_time(p))
                              , str(get_remaining_time(p,ta))
                                 ))
                
                for s in p.sesshun_set.all():
                    outfile.write("\n\t\t %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %\
                                       (str(s.schedulable())
                                     , s.name.ljust(14)
                                     , s.observing_type.type.ljust(13)
                                     , s.session_type.type.ljust(9)
                                     , str(s.frequency)
                                     , str(s.allotment.total_time)
                                     , str(ta.getTimeLeft(s))
                                     , str(s.min_duration)
                                     , str(s.max_duration)
                                     , str(s.time_between)
                                        )
                                  )
                    
        else:
            outfile.write("\n\t None")

if __name__=='__main__':
    start = datetime.today()
    GenerateReport(start)

