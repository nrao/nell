from sesshuns.models import *

class ScheduleTools(object):

    def changeSchedule(self, start, duration, sesshun, reason, description):
        """
        Change the schedule, and take care of all the time accounting.
        This is meant for use in such cases as examplified in Memo 11.2.
        Right now, this only handles substituting one session for one
        or more sessions, where the time taken is accounted to one of these
        Reasons:
            time to other session due to weather
            time to other session due to rfi
            time to other session due to other reason
        and the time given to the new session is marked as short notice.
        Note that the times are not *assigned*, but instead times and descs.
        are incremented, so as not to overwrite previous changes.
        """

        # what periods are we affecting?
        duration_mins = duration * 60.0
        ps = Period.get_periods(start, duration_mins)

        # first, adjust each of the affected periods - including time accnting
        end = start + timedelta(hours = duration)
        for p in ps:
            if p.start >= start and p.end() <= end:
                # this entire period is being replaced
                # TBF: can't do this p.delete()
                # TBF: use state!
                p.duration = 0
                #p.delete()
                #p = None
            elif p.start < start and p.end() > start:
                # we're chopping off the end of this period
                p.duration = (start - p.start).seconds / 3600.0
            elif p.start >= start and p.end() > end:
                # we're chopping off the beginning of this period
                p.duration = (p.end() - end).seconds / 3600.0
                p.start = end
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
                # increment values: don't overwrite them!
                value = p.accounting.get_time(reason)
                p.accounting.set_changed_time(reason, value + duration)
                desc = p.accounting.description \
                    if p.accounting.description is not None else ""
                nowStr = datetime.now().strftime("%Y-%m-%d %H:%M")    
                desc += " [Schedule Change (%s)]: " % nowStr
                p.accounting.description = desc + description
                p.accounting.save()
                p.save()

        # finally, anything to replace it with?
        if sesshun is not None:
            # create a period for this
            pa = Period_Accounting(scheduled    = duration
                                 , short_notice = duration
                                 , description  = description)
            pa.save()                     
            p = Period(session    = sesshun
                     , start      = start
                     , duration   = duration
                     , score      = 0.0
                     , forecast   = start
                     , accounting = pa)
            p.save()    

      # TBF: now we have to rescore all the affected periods!
