from sesshuns.models import *
from datetime        import datetime, timedelta

class TimeAccounting:

    """
    This class is responsible for calculating some of the equations specified in
    Memo 11.2.
    """

    def getProjectTotalTime(self, proj):
        return sum([a.total_time for a in proj.allotments.all()])

    def getProjSessionsTotalTime(self, proj):
        ss = proj.sesshun_set.all()
        return sum([s.allotment.total_time for s in ss])

    def getObservedProjTime(self, proj):
        ss = proj.sesshun_set.all()
        return sum([self.getObservedTime(s) for s in ss])

    def getObservedTime(self, sess):
        now = datetime.utcnow()
        ps = sess.period_set.all()
        return sum([p.accounting.observed() for p in ps if p.end() < now])
        
    def getTimeLeft(self, sess):
        obs = self.getObservedTime(sess)
        return sess.allotment.total_time - obs

    def changeSchedule(self, start, duration, sesshun, reason, description):
        """
        Change the schedule, and take care of all the time accounting.
        This is meant for use in such cases as examplified in Memo 11.2.
        Reasons:
          Sesshun is None:
            lost time due to weather
            lost time due to rfi
            lost time due to other reason
          Sesshun is not None:
            time to other session due to weather
            time to other session due to rfi
            time to other session due to other reason
        """

        duration_hrs = duration/60.0

        # what periods are we affecting?
        ps = Period.get_periods(start, duration)

        # first, adjust each of the affected periods - including time accnting
        end = start + timedelta(minutes = duration)
        for p in ps:
            if p.start >= start and p.end() <= end:
                # this entire period is being replaced
                # TBF: can't do this p.delete()
                #p.duration = 0
                p.delete()
                p = None
            elif p.start < start and p.end() > start:
                # we're chopping off the end of this period
                p.duration = (start - p.start).seconds / 3600.0
            elif p.start >= start and p.end() > end:
                # we're chopping off the beginning of this period
                p.start = start
            elif p.start < start and p.end() > end:
                # TBF
                raise "Not implemented yet."
                # we're chopping out the middle of a period: we fix this
                # by adjusting the period, then creating a new one
                original_duration = p.duration
                original_end      = p.end()
                p.duration = (start - p.start).seconds / 36000.0
                # the new one
                #new_dur = (original_end - end).minutes
                #new_p = Period(session  = p.session
                #         , start    = end
                #         , duration = new_dur
                #         , accounting = Period_Accounting(scheduled = new_dur)
                #         )
            else:
                raise "not covered"
            # now change this periods time accounting
            if p is not None:
                p.accounting.set_changed_time(reason, duration_hrs)
                p.accounting.description = description
                p.accounting.save()
                p.save()

        # finally, anything to replace it with?
        if sesshun is not None:
            # create a period for this
            pa = Period_Accounting(scheduled    = duration_hrs
                                 , short_notice = duration_hrs
                                 , description  = description)
            pa.save()                     
            p = Period(session    = sesshun
                     , start      = start
                     , duration   = duration_hrs
                     , score      = 0.0
                     , forecast   = start
                     , accounting = pa)
            p.save()    

        # TBF: now we have to rescore all the affected periods!
