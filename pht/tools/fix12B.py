from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler import models as dss
from pht       import models as pht
from pht.tools.database import DssExport

export = DssExport()
for p in dss.Project.objects.filter(semester__semester = '12B').exclude(pcode__contains = 'TGBT'):
    print "Fixing", p.pcode
    for s in p.sesshun_set.all():
        pht_s = pht.Session.objects.get(name = s.name)
        pht_s.dss_session = s
        pht_s.save()
        for pr in s.period_set.all():
            pa = dss.Period_Accounting(scheduled = 0.0)
            pa.save()
            pr.accounting = pa
            pr.score = -1.0
            pr.save()
            export.addPeriodReceivers(pr, [r.abbreviation for r in pht_s.receivers.all()])
print "done."
