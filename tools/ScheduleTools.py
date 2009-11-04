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

    def shiftPeriodBoundaries(self, period, start_boundary, time, neighbor, desc):
        """
        Shifts the boundary between a given period and it's neighbors:
           * period_id - the period obj. whose boundary we first adjust
           * start_boundary - boolean, true for start, false for end
           * time - new time for that boundary
           * neighbors - periods affected
        After periods are adjusted, time accounting is adjusted appropriately
        """

        # TBF, HACK, DEBUG, WTF: this code sucks, the four cases covered
        # by the 'if' conditionals have lots of redundant code and must
        # be refacatored.

        # create the tag used for all descriptions in time accounting
        nowStr = datetime.now().strftime("%Y-%m-%d %H:%M")    
        tag = " [Shift Period Bnd. (%s)]: " % nowStr 

        # get the time range affected
        original_time = period.start if start_boundary else period.end()

        # check for the no-op
        if original_time == time:
            return

        if start_boundary:
            # changing when the period starts: don't start it after
            # this period ends
            assert time < period.end()
            period.start = time
            if original_time > time:
                # starting the period early!
                diff_hrs = ((original_time - time).seconds) / (60.0*60.0)
                period.accounting.short_notice = diff_hrs
                period.accounting.scheduled += diff_hrs
                period.start = time
                period.duration += diff_hrs
                # take away from the neighbors - who are?

                ps = Period.get_periods(time, diff_hrs * 60.0)
                for p in ps:
                    # ignore the original period
                    if p.id == period.id:
                        continue
                    # if the period is completely overridden by new boundary
                    # remove it
                    if p.start >= time:
                        p.accounting.other_session_other = p.duration
                        p.accounting.description = tag + desc
                        p.accounting.save()
                        p.duration = 0.0 # TBF: state!
                        p.save()
                    else:
                        p.accounting.other_session_other = diff_hrs 
                        p.accounting.description = tag + desc
                        p.accounting.save()
                        p.duration = (time - p.start).seconds / (60.0*60.0)
                        p.save()
            else:            
                # starting the period later!            
                diff_hrs = ((time - original_time).seconds) / (60.0*60.0)
                period.accounting.other_session_other = diff_hrs
                period.accounting.description = tag + desc
                period.start = time
                period.duration -= diff_hrs
                # giving to the neighbor: just the period that started
                # before:
                neighbor.accounting.short_notice = diff_hrs
                neighbor.accounting.scheduled += diff_hrs
                neighbor.accounting.description = tag + desc
                neighbor.accounting.save()
                neighbor.duration += diff_hrs
                neighbor.save()
        else:
            # changing when the period ends. 
            # this period ends
            assert time > period.start
            if original_time > time:
                # shrinking the period! 
                diff_hrs = ((original_time - time).seconds) / (60.0*60.0)
                period.accounting.other_session_other = diff_hrs
                period.accounting.description = tag + desc
                period.accounting.save()
                period.duration = ((time - period.start).seconds) / (60.0*60.0) 
                # giving to the neighbors - who are?
                neighbor.accounting.short_notice = diff_hrs
                neighbor.accounting.scheduled += diff_hrs
                neighbor.accounting.description = tag + desc
                neighbor.accounting.save()
                neighbor.start = time
                neighbor.duration += diff_hrs
                neighbor.save()
            else:
                # period is growing! at whose expense?
                diff_hrs = ((time - original_time).seconds) / (60.0*60.0)
                period.accounting.scheduled += diff_hrs
                period.accounting.short_notice = diff_hrs
                period.accounting.description = tag + desc
                period.accounting.save()
                period.duration = ((time - period.start).seconds) / (60.0*60.0)
                ps = Period.get_periods(time, diff_hrs * 60.0)
                for p in ps:
                    # ignore the original period
                    if p.id == period.id:
                        continue
                    # if the period is completely overridden by new boundary
                    # remove it
                    if p.end() <= time:
                        p.accounting.other_session_other = p.duration
                        p.accounting.description = tag + desc
                        p.accounting.save()
                        p.duration = 0.0 # TBF: state!
                        p.save()
                    else:
                        p.accounting.other_session_other = diff_hrs 
                        p.accounting.description = tag + desc
                        p.accounting.save()
                        p.start = time
                        p.duration -= diff_hrs 
                        p.save()

        period.accounting.save()
        period.save()

                        

                

