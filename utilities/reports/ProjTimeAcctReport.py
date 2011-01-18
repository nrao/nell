#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from nell.tools.TimeAccounting import TimeAccounting
from sesshuns.models           import Project, first
import sys

def GenerateProjectTimeAccountingReport(pcode):

    project = first(Project.objects.filter(pcode = pcode)) 
    if project is None:
        print "cannot find project: ", pcode
        return
    ta = TimeAccounting()
    ta.report(project, "%sTimeAccounting.txt" % pcode)

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        pcode = sys.argv[1]
        print pcode
        GenerateProjectTimeAccountingReport(pcode)
    else:
        print "must provide project code"
