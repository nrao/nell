from nell.utilities.database.external import UserInfo, PSTMirrorDB
from scheduler.models import *

# Utility for taking in a list of usernames from computing, and 
# seeing who should be deleted and who shouldn't

pst = PSTMirrorDB()


filename = 'oldUsers.txt'

f = open(filename, 'r')
lines = f.readlines()
notInPst = []
notInDss = []
scheduled = []
notScheduled = []
notComplete = []
for l in lines:
    username = l.split(" ")[0].strip()
    pst_id = None
    u = None
    try:
        pst_id = pst.getIdFromUsername(username)
    except:
        pst_id = None
        notInPst.append(username)
    if pst_id is not None:    
        try:
            u = User.objects.get(pst_id = pst_id)
        except:
            u = None
            notInDss.append(username)
    if u is not None:
        notCmps = [pcode for pcode in u.getProjects() if not Project.objects.get(pcode = pcode).complete]
        if len(notCmps) > 0:
            print "   ", username
            notComplete.append(username)
        if len(u.getUpcomingPeriods()) > 0:
            scheduled.append(username)
        else:
            notScheduled.append(username)
f.close()

print "Checking %d users." % len(lines)
print ""
print "Users with incomplete projects: "
for u in notComplete:
    print u
print ""    
print "Scheduled Users: "
for u in scheduled:
    print u
print ""
print "Users NOT scheduled: "
for u in notScheduled:
    print u
print ""
print "Users not PST:"
for u in notInPst:
    print u
print "Total: ", len(notInPst)
print ""
print "Users not DSS:"
for u in notInDss:
    print u
print "Total: ", len(notInDss)
