from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *
from tools.TimeAccounting import TimeAccounting
from sets                 import Set
from datetime             import *
from sesshuns.templatetags.custom import *

from Report import Report, Line



project_header = ["pcode",
                  "name",
                  "PI",
                  "tot hrs",
                  "sess hrs",
                  "tb",
                  "tb fut",
                  "rem"]

session_header = ["sch",
                  "cmp",
                  "enbl",
                  "auth",
                  "name",
                  "orgID",
                  "obs type",
                  "type",
                  "freq",
                  "RA",
                  "Dec",
                  "tot",
                  "tbctp",
                  "tbfut",
                  "rem",
                  "min",
                  "max",
                  "rcvrs"]

fptype = type(1.0)

def bl2(value, ch):
    return ch if value else ''


def GenerateReport(start):
    sorted_semesters=sorted(Semester.objects.all(),lambda x,y:cmp(x.semester,y.semester))
    ta = TimeAccounting()

    for s in sorted_semesters:
        print "\n Trimester : %s" % (s.semester)
        print "----------------"

        the_projects=[p for p in s.project_set.all() if not p.complete]
        projects = sorted(the_projects, lambda x, y: cmp(x.pcode, y.pcode))
        if projects:

            rep = Report()
            line = Line()

            for i in project_header:
                line.add(i)

            rep.add_headers(line)

            for p in projects:
                line.clear()
                line.add(p.pcode)
                line.add(p.name[:50])
                line.add(p.principal_investigator().last_name)
                line.add(ta.getProjectTotalTime(p), fptype)
                line.add(ta.getProjSessionsTotalTime(p), fptype)
                line.add(ta.getCompletedTimeBilled(p), fptype)
                line.add(ta.getUpcomingTimeBilled(p), fptype)
                line.add(ta.getTimeRemainingFromCompleted(p), fptype)
                rep.add_line(line)
                line.clear()

                for i in session_header:
                    line.add(i)
                    
                rep2 = Report()
                rep2.add_headers(line)

                sess = sorted(p.sesshun_set.all(), \
                           lambda x,y:cmp(x.name, y.name))
                for s in sess:

                    line.clear()
                    line.add(bl2(s.schedulable(), 'Y'))
                    line.add(bl2(s.status.complete, 'C'))
                    line.add(bl2(s.status.enabled, 'E'))
                    line.add(bl2(s.status.authorized, 'A'))
                    line.add(s.name[:25])
                    line.add(s.original_id)
                    line.add(s.observing_type.type)
                    line.add(s.session_type.type[0])
                    line.add(s.frequency)
                    line.add(target_horz(s))
                    line.add(target_vert(s))
                    line.add(s.allotment.total_time)
                    line.add(ta.getCompletedTimeBilled(s), fptype)
                    line.add(ta.getUpcomingTimeBilled(s), fptype)
                    line.add(ta.getTimeRemainingFromCompleted(s), fptype)
                    line.add(s.min_duration, fptype)
                    line.add(s.max_duration, fptype)
                    line.add("".join(s.rcvrs_specified()))
                    rep2.add_line(line)

                rep.add_report(rep2)
            rep.output()
        else:
            print "\t None"

if __name__=='__main__':
    start = datetime.today()
    GenerateReport(start)

