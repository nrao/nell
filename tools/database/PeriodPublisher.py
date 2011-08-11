from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import *
from datetime import datetime, timedelta 
import sys

def getPeriodsNeedPublished(start, end):
    return Period.objects.filter(start__gt = start
                               , start__lt = end
                               , state__abbreviation = "P")

if __name__ == '__main__':

    days = int(sys.argv[1])
    start = datetime.now()
    end = start + timedelta(days = days)

    ps = getPeriodsNeedPublished(start, end)
    print "Num periods to publish: ", len(ps)

    numPs = len(ps)
    while numPs > 0:
        p = ps[0]
        p.publish()
        p.save()
        ps      = getPeriodsNeedPublished(start, end)
        prevNum = numPs
        numPs   = len(ps)
        assert numPs < prevNum

    print "done!" 
