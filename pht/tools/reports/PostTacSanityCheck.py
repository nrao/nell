
from django.core.management import setup_environ
import settings
setup_environ(settings)

from pht.models import *
from pht.httpadapters import SessionHttpAdapter

class PostTacSanityCheck (object):

    def __init__(self):
        self.ids = [1120, 1089, 1122, 1123, 1125, 1129, 1162, 1131,
                1100, 1071, 1137, 1138, 1150, 1289, 1114, 1151, 1146, 1118, 1119]

    def checkDB(self):
        proposals = [Proposal.objects.get(id = id) for id in self.ids]
        print "Modified Proposals: ", ', '.join([p.pcode for p in proposals])
        for p in proposals:
            print "PCode\t\tRq.\tAllot."
            print "%s\t%s\t%s" % (p.pcode, p.requestedTime(), p.allocatedTime())

            print "\tName\t\tGrade\tRq.\tAllot."
            for s in p.session_set.all().order_by('name'):
                sa = SessionHttpAdapter(s)
                data = sa.jsonDict()
                print "\t%s\t%s\t%s\t%s" % (data['name'], data['grade'], data['requested_total'], data['allocated_time'])

if __name__ == '__main__':
    check = PostTacSanityCheck()
    check.checkDB()
