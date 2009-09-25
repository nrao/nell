from   datetime  import timedelta
import TimeAgent

def gen_gbt_schedule(start, end, days, timezone, periods):
    # construct the calendar - we are getting a little bit into presentation
    # detail here, but that's mostly because the timezone business sucks.
    cal = {}
    for i in range(days):
        day = day_tz = start + timedelta(days = i)
        day_tz = TimeAgent.est2utc(day_tz) if timezone == 'ET' else day_tz
        cal[day] = [get_period_day_time(day, p, start, end, timezone) \
                    for p in periods if p.on_day(day_tz)]
    return cal

def get_period_day_time(day, period, first_day, end, timezone):
    "Returns a tuple of : start, end, cutoffs, period, for use in template"
    last_day = end - timedelta(days = 1)
    next_day = day + timedelta(days = 1)
    # start with default values - as if there was no overlap
    start = period.start
    end = period.end()
    if timezone == 'ET':
        start = TimeAgent.utc2est(start)
        end = TimeAgent.utc2est(end)
    start_cutoff = end_cutoff = False
    # but does this period overlap the given day?
    if start < day or end >= next_day:
        # oh, crap, overlap - cut off the dates 
        if start < day:
            start = day
            # will the beginning of this period not be displayed?    
            if day == first_day:
                start_cutoff = True
        if end >= next_day:
            end = next_day
            # will the end of this period not be displayed?    
            if day == last_day:
                end_cutoff = True
    #startStr = start.strftime("%H:%M")            
    #endStr = end.strftime("%H:%M")                
    return (start, end, start_cutoff, end_cutoff, period)
