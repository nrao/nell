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

        # get rid of this once develompent has stablized.
        debug = False

        # tag the descriptoin
        nowStr = datetime.now().strftime("%Y-%m-%d %H:%M")    
        tag = " [Schedule Change (%s)]: " % nowStr 
        description = tag + description

        # what periods are we affecting?
        duration_mins = duration * 60.0
        ps = Period.get_periods(start, duration_mins)
        if debug:
            print "len(ps): ", len(ps)

        # first, adjust each of the affected periods - including time accnting
        end = start + timedelta(hours = duration)
        for p in ps:
            if debug:
                print "changing period: ", p
                print "comparing period: ", p.start, p.end()
                print "w/:               ", start, end 
            if p.start >= start and p.end() <= end:
                if debug:
                    print "delete period!"
                # this entire period is being replaced
                # TBF: can't do this p.delete()
                # TBF: use state!
                other_sess_time = p.duration
                p.duration = 0
                #p.delete()
                #p = None
            elif p.start >= start and p.end() > end:
                if debug:
                    print "start period later"
                # we're chopping off the beginning of this period
                new_duration = (p.end() - end).seconds / 3600.0
                other_sess_time = p.duration - new_duration
                p.duration = new_duration
                p.start = end
            elif p.start < start and p.end() > end:
                if debug:
                    print "bi-secting period"
                # we're chopping out the middle of a period: we fix this
                # by adjusting the period, then creating a new one
                original_duration = p.duration
                original_end      = p.end()
                p.duration = (start - p.start).seconds / 3600.0
                # the new one
                new_dur = (original_end - end).seconds / 3600.0
                accounting = Period_Accounting(scheduled = new_dur
                                             , short_notice = new_dur
                                             , description = description
                                               )
                accounting.save()                             
                period_2cd_half = Period(session  = p.session
                                       , start    = end
                                       , duration = new_dur
                                       , score    = 0.0
                                       , forecast = end
                                       , accounting = accounting 
                                         )
                period_2cd_half.save()                         
                # the original period is really giving up time to the 
                # bi-secting new period, and the new second half!
                other_sess_time = duration + new_dur
            elif p.start < start and p.end() > start:
                if debug:
                    print "shorten period"
                # we're chopping off the end of this period
                new_duration = (start - p.start).seconds / 3600.0
                other_sess_time = p.duration - new_duration
                p.duration = new_duration
                         
            else:
                raise "not covered"
            # now change this periods time accounting
            if p is not None:
                if debug:
                    print "changes: ", p
                # increment values: don't overwrite them!
                value = p.accounting.get_time(reason)
                p.accounting.set_changed_time(reason, value + other_sess_time)
                desc = p.accounting.description \
                    if p.accounting.description is not None else ""
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
