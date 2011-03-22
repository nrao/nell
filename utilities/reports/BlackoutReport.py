#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime        import datetime, timedelta
from scheduler.models import *
from nell.utilities  import TimeAgent

def GenerateBlackoutReport():
    outfile = open("./DssBlackoutReport.txt", 'w')
    now     = datetime.utcnow()
    later   = now + timedelta(days = 7)

    outfile.write("Project     | Start (UTC) |  End (UTC)  |  Start (ET) |  End (ET)\n")
    outfile.write("-------------------------------------------------------------------\n")

    sorted_projects = sorted(Project.objects.filter(complete = False)
                           , lambda x, y: cmp(x.pcode, y.pcode))
    for p in sorted_projects:
        blackouts = p.get_blackout_times(now, later)
        if blackouts:
            for start, end in blackouts:
                outfile.write("%s | %s | %s | %s | %s\n" % \
                    (p.pcode.ljust(11)
                   , start.strftime("%m-%d %H:%M")
                   , end.strftime("%m-%d %H:%M")
                   , TimeAgent.utc2est(start).strftime("%m-%d %H:%M")
                   , TimeAgent.utc2est(end).strftime("%m-%d %H:%M")))

    outfile.close()

if __name__ == '__main__':
    GenerateBlackoutReport()
