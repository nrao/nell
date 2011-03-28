from datetime import datetime
from scheduler.models import *
import reversion
from reversion.models import Version
from reversion import revision
from utilities.VersionDiff import VersionDiff
from utilities.RevisionUtility import RevisionUtility
from utilities.RevisionUtilityTester import RevisionUtilityTester
from utilities   import TimeAgent

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
           # the revision library saves things in ET - but we deal in UT    
           if not self.test:
               dt = TimeAgent.est2utc(v.revision.date_created)    
           else:
               # why make setting up the tests anymore complicated?
               dt = v.revision.date_created
           state = (dt, currentState)   
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
       diffs = [d for d in allDiffs if d.timestamp(self.test) >= newChangesDt \
           and d.timestamp(self.test) > mostRecentPublishDate \
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


