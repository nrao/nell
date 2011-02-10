from sesshuns.models import *
import reversion
from reversion.models import Version
from reversion import revision
from VersionDiff import VersionDiff
from RevisionUtility import RevisionUtility
from RevisionUtilityTester import RevisionUtilityTester

class PeriodChanges:

    def __init__(self, test = False):

        self.test = test
        if not test:
            self.revisions = RevisionUtility()
        else:
            self.revisions = RevisionUtilityTester()

        # if one of these fields in Period, Period_Accounting
        # changes, there's no need to notify anyone of it
        self.ignoreFields = ['moc_ack'
                           , 'score'
                           , 'forecast'
                           , 'backup'
                           , 'window'
                           , 'elective'
                           , 'description'
                           , 'last_notification'] 

    def getStates(self, periodVersions):
       "What is the state history: a list of (dates, current state of period)?"
       states = []
       currentState = None
       for v in periodVersions:
           state = v.field_dict.get("state", None)
           if state is not None:
               currentState = state
           state = (v.revision.date_created, currentState)   
           if state not in states:
               states.append(state)
       return states        

    def getChangesForNotification(self, period):
       "Returns VersionDiff's that warrant a new notification for this period."

       # here we only care about how the period state has changed
       # over time, so just get the Period's versions
       vs = self.revisions.getVersions(period)

       newChangesDt, states = self.getNewChangeDate(period, vs)

       # check if any kinds of change were detected at all
       if len(states) == 0 or newChangesDt is None:
           # if not, there's no diffs either then
           return []

       mostRecentPublishDate = self.getMostRecentPublishDate(states)
           
       allDiffs = self.getAllPeriodDiffs(period)

       # finally, here's where all this (too much) info gets filtered.
       # we want to return only those diffs that warrant a new notification.
       # And what warrants a new notification?:
       #   * it's a change in one of the non-ignore fields
       #      - for example, who cares if someone added more detail to the
       #        accounting description field.
       #   * the change happened since the most publication date
       #   * the change happened since the newest changes
       diffs = [d for d in allDiffs if d.dt >= newChangesDt \
           and d.dt > mostRecentPublishDate \
           and d.field not in self.ignoreFields]
       return diffs

    def getAllPeriodDiffs(self, period):
       """
       For the given period, returns a list of VersionDiff objects that
       capture all the relevant changes to this Period and it's related
       objects.
       In this case, the accounting object is the only 'related' object
       we care about - we're explicity ignoring the periods receivers.
       """
       diffs = self.revisions.getObjectDiffs(period)
       diffs.extend(self.revisions.getObjectDiffs(period.accounting))
       diffs.sort(key=lambda x: x.dt)
       return diffs

    def getMostRecentPublishDate(self, states):
       """
       Given a list of (datetime, period state), get the most recent
       date at which the period was published (moved to the scheduled
       state).
       """
       publishDTs = []
       prevState = originalState = states[0][1]
       for dt, state in states:
           if state == 2 and prevState != 2:
               publishDTs.append(dt)
           prevState = state    

       if len(publishDTs) == 0:
           if originalState == 2:
               mostRecentPublishDT = states[0][0]
           else:
               mostRecentPublishDT = datetime(2100, 1, 1) # end of time 
       else:
           mostRecentPublishDT = publishDTs[-1]
       return mostRecentPublishDT

    def hasBeenScheduled(self, period):
       print ""
       print "hasBeenScheduled: "
       print period

       vs = self.revisions.getVersions(period)
       vs.extend(self.revisions.getVersions(period.accounting))
       # sort by revision date
       vs.sort(key=lambda x: x.revision.date_created)

       print "hasBeenScheduled versions: ", len(vs)
       for v in vs:
           print " ", v

       trackFromDt, states = self.stateHistory(period, vs)
       if len(states) == 0:
           return []

       # find the publish (other state -> scheduled) states
       publishDTs = []
       prevState = originalState = states[0][1]
       for dt, state in states:
           if state == 2 and prevState != 2:
               publishDTs.append(dt)
           prevState = state    

       if len(publishDTs) == 0:
           if originalState == 2:
               mostRecentPublishDT = states[0][0]
           else:
               mostRecentPublishDT = datetime(2100, 1, 1) # next century 
       else:
           mostRecentPublishDT = publishDTs[-1]
           
       # get pertinent diffs
       #diffs = [d for d in self.getObjectDiffs(period) if d.dt >= trackFromDt]
       diffs = self.revisions.getObjectDiffs(period)
       diffs.extend(self.revisions.getObjectDiffs(period.accounting))
       diffs.sort(key=lambda x: x.dt)
       print "hasBeenScheduled diffs: "
       for d in diffs:
           print d

       ignore_fields = ['moc_ack', 'score', 'forecast', 'backup', 'window', 'elective', 'description', 'last_notification'] 
       if trackFromDt is not None:
           diffs = [d for d in diffs if d.dt >= trackFromDt and d.dt > mostRecentPublishDT and d.field not in ignore_fields]
       else:
           diffs = []
       

       for d in diffs:
           print d

       #self.reportObject(period)
       #self.reportObject(period.accounting)
       #print period
       #print "number of diffs to report for this period: ", len(diffs)
       #print ""
       return diffs

    def getNewChangeDate(self, period, vs):
       """
       Given a period and it's revision history (versions), when was
       the ealiest change made since the last time a notification
       was sent out, that affected the period when it was Scheduled?
       """
       states = self.getStates(vs)

       # When was the last time a notification was sent for this period?
       lastNoticeDT = period.last_notification
       if lastNoticeDT is None:
           lastNoticeDT = datetime(2000, 1, 1) # beginning of time

       # What is the ealriest date in which a change was made to a 
       # scheduled period on a date
       # since the last notification?
       scheduledYet = False
       i = 0
       for i in range(len(states)):
           if states[i][1] == 2:
               scheduledYet = True
           if states[i][0] > lastNoticeDT and scheduledYet:
               break
           else:
               i += 1
       if i < len(states):
           affectedDT = states[i][0]
       else:
           affectedDT = None
       
       #print "last notificaiton: ", lastNoticeDT
       #print "start tracking at: ", affectedDT

       return (affectedDT, states)

    def stateHistory(self, period, vs):

       # what is the state history?
       #states = [(v.revision.date_created, v.field_dict.get("state", None)) for v in vs]
       states = []
       currentState = None
       for v in vs:
           state = v.field_dict.get("state", None)
           if state is not None:
               currentState = state
           states.append((v.revision.date_created, currentState))    

       for s in states:
           print s[0], s[1] #, Period_State.objects.get(id = int(s[1]))

       # TBF: fake the last notification time
       #lastNoticeDT = datetime.now() - timedelta(days = 7)
       lastNoticeDT = period.last_notification
       if lastNoticeDT is None:
           lastNoticeDT = datetime(2000, 1, 1)

       # report on any changes since the last notice that
       # affected a scheduled period
       scheduledYet = False
       i = 0
       for i in range(len(states)):
           if states[i][1] == 2:
               scheduledYet = True
           if states[i][0] > lastNoticeDT and scheduledYet:
               break
           else:
               i += 1
       
       if i < len(states):
           affectedDT = states[i][0]
       else:
           affectedDT = None
       
       print "last notificaiton: ", lastNoticeDT
       print "start tracking at: ", affectedDT

       return (affectedDT, states)
