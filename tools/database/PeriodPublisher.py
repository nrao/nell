from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import *
from datetime import datetime 

def getPeriodsNeedPublished():
    return Period.objects.filter(start__gt = datetime.now(), state__abbreviation = "P")

if __name__ == '__main__':
    ps = getPeriodsNeedPublished()
    print "Num periods to publish: ", len(ps)

    numPs = len(ps)
    while numPs > 0:
        p = ps[0]
        p.publish()
        p.save()
        ps      = getPeriodsNeedPublished()
        prevNum = numPs
        numPs   = len(ps)
        assert numPs < prevNum

    print "done!" 
