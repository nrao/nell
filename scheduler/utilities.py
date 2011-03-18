from scheduler.models import *

def get_rev_comment(request, obj, method):
    className = obj.__class__.__name__ if obj is not None else ""
    where = "%s %s" % (className, method)
    who   = request.user.username
    return "WHO: %s, WHERE: %s" % (who, where)

def getInvestigatorEmails(pcodes):
    """
    Given a list of project codes, what are the list of emails for them
    organized by:
       * Principal Investigator
       * Principal Contact
       * Co-Investigatrs
       * Observers
       * Friends
    """   
    pi = []
    pc = []
    ci = []
    ob = []
    fs = []
    try:
        # TBF: use list comprehension?
        for pcode in pcodes:
            p = Project.objects.filter(pcode = pcode)[0]
            for inv in p.investigator_set.all():
                if inv.principal_investigator:
                    for email in inv.user.getEmails():
                        pi.append(email)
                if inv.principal_contact:
                    for email in inv.user.getEmails():
                        pc.append(email)
                if not inv.principal_investigator and not inv.principal_contact:
                    for email in inv.user.getEmails():
                        ci.append(email)
                if inv.observer:
                    for email in inv.user.getEmails():
                        ob.append(email)
            for f in p.friend_set.all():                        
                for email in f.user.getEmails():
                    fs.append(email)
    except IndexError, data:
        pass # in case of blanks at the end of the list.
    return sorted(pi), sorted(pc), sorted(ci), sorted(ob), sorted(fs)

