from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models              import *
from nell.utilities.TimeAccounting    import TimeAccounting
from sets                         import Set
from datetime                     import *
from sesshuns.templatetags.custom import * # TBF: NO! NO!
import sys

from nell.utilities.reports.Report import Report, Line

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

    blank_line = Line()
    blank_line.add(" ")
    prj_head = Line()
    sess_head = Line()

    for i in project_header:
        prj_head.add(i)

    for i in session_header:
        sess_head.add(i)
                
    for s in sorted_semesters:
        print "\n Trimester : %s" % (s.semester)
        print "----------------"

        the_projects = [p for p in s.project_set.all() if not p.complete]
        projects = sorted(the_projects, lambda x, y: cmp(x.pcode, y.pcode))

        if projects:

            tri_report = Report()
            line = Line()

            for p in projects:

                prj_report = Report()
                prj_report.add_headers(prj_head)
                line.clear()
                line.add(p.pcode)
                line.add(p.name[:50])

                pi = p.principal_investigator()
                line.add(pi.last_name if pi else "No PI assigned!")
                line.add(ta.getProjectTotalTime(p), fptype)
                line.add(ta.getProjSessionsTotalTime(p), fptype)
                line.add(ta.getCompletedTimeBilled(p,start), fptype)
                line.add(ta.getUpcomingTimeBilled(p,start), fptype)
                line.add(ta.getTimeRemainingFromCompleted(p,start), fptype)
                prj_report.add_line(line)
                tri_report.add_report(prj_report)
                tri_report.add_line(blank_line)
                line.clear()

                sess_report = Report()
                sess_report.add_headers(sess_head)

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
                    line.add(ta.getCompletedTimeBilled(s, start), fptype)
                    line.add(ta.getUpcomingTimeBilled(s, start), fptype)
                    line.add(ta.getTimeRemainingFromCompleted(s, start), fptype)
                    line.add(s.min_duration, fptype)
                    line.add(s.max_duration, fptype)
                    line.add("".join(s.rcvrs_specified()))
                    sess_report.add_line(line)

                tri_report.add_report(sess_report)
                tri_report.add_line(blank_line)
                tri_report.add_line(blank_line)
                tri_report.add_line(blank_line)
            tri_report.normalize()
            tri_report.output()
        else:
            print "\t None"

if __name__=='__main__':

    # use today for the start time, or the passed in time
    if len(sys.argv) > 1:
        try:
            opt = sys.argv[1]
            parts = opt.split("=")
            start = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S")
        except:
            print 'Option must be -start="YYYY-mm-dd HH:MM:SS"'
            sys.exit()
    else:
        start = datetime.today()

    GenerateReport(start)

