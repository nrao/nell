from sesshuns.models import *
#import reversion
from reversion.models import Version
#from reversion import revision
from revisionReport import RevisionReport

class SessionRevReport(RevisionReport):

    def __init__(self):
        #super(RevisionReport, self)

        self.relatedClasses = ['Receiver_Group'
                             , 'Receiver'
                             , 'Status'
                             , 'Target'
                             , 'Allotment'
                              ]

    def getSessionRcvrDiffs(self, pcode, name):
        """
        Rcvrs for Session and Periods are deleted and readded every time a change is made,
        so tracking their changes takes a lot of interpretation.
        """
        diffs = []
        s = self.getSession(pcode, name)
        # TBF: get current recievrs for last check
        currentRgs = s.receiver_group_set.all()
        # get all the deleted Rcvr_Groups for this session
        id = s.id
        vs = Version.objects.get_deleted(Receiver_Group)
        svs = []
        for v in vs:
            if v.field_dict['session'] == id:
                svs.append(v)
                #print v.revision.date_created
                #print v.field_dict['receivers']
    
        #print "svs: ", svs
        # Now get the diffs, but keep only those that pertain to receivers
        if len(svs) < 2:
           return diffs
        vprev = svs[0]
        for v in svs[1:]:
            ds = self.diffVersions(vprev, v)
            for d in ds:
                if d[1] == "receivers":
                    diffs.append(self.interpretRcvrGrpDiff(d))
            vprev = v
    
        # TBF: see if the last diff is different then our current rcvrs
        if len(currentRgs) == 1 and len(diffs) > 0:
            # anything else is too complicated (TBF)
            rcvrs = [r.abbreviation for r in currentRgs[0].receivers.all()]
            rcvrs.sort()
            lastRs = diffs[-1][3]
            lastRs.sort()
            if rcvrs != lastRs:
                diffs.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "receivers", lastRs, rcvrs))
    
        return diffs             
    
    def getSessionRcvrDiffsBad(self, pcode, name):
    
        diffs = []
        s = self.getSession(pcode, name) 
        vs = Version.objects.get_for_object(s)
        if len(vs) < 2:
            return []
        vprev = vs[0]
        for v in vs[1:]:
            print "v: ", v
            prevS = vprev.object_version.object
            currS = v.object_version.object
            v1 = prevS.receiver_list()
            v2 = currS.receiver_list()
            print "comparing: ", v1, v2
            if v1 != v2:
                dt = vprev.revision.date_created
                diffs.append((dt, "receivers", v1, v2))
        
    
        return diffs
            
    
    def reportSessionDiffs(self, pcode, name, periods = False):
    
        diffs = []
        s = self.getSession(pcode, name) 
        if s is None:
            print "Could not find Session"
            return
        diffs.extend(self.getObjectDiffs(s)) 
        diffs.extend(self.getObjectDiffs(s.allotment))
        for t in s.target_set.all():
            diffs.extend(self.getObjectDiffs(t))
        diffs.extend(self.getObjectDiffs(s.status))
        diffs.extend(self.getSessionRcvrDiffs(pcode, name))
        diffs.sort()    
        for d in diffs:
            print "(%s) field %s: %s -> %s" % (d[0], d[1], d[2], d[3])
        if periods:
            ps = s.period_set.all()
            for p in ps:
                "****** Diffs for Period: %s", p
                self.reportPeriodDiffs(p.id)

    def getSession(self, pcode, name):
        ss = Sesshun.objects.filter(name = name)
        s = first([s for s in ss if s.project.pcode == pcode])
        return s
    
    def reportSession(self, pcode, name, time = None, field = None, periods = False):
        s = self.getSession(pcode, name) 
        self.reportObject(s, time, field)
        print "Diffs: "
        self.reportSessionDiffs(pcode, name, periods)

    def reportSessionForTime(self, pcode, name, timeStr):
        s = self.getSession(pcode, name) 
        self.reportObjectForTime(s, timeStr)
                
