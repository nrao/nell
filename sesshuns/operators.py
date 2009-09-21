from datetime                       import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts         import render_to_response
from models                   import *
from sets                     import Set
from utilities                import gen_gbt_schedule, UserInfo

# persist this object to avoid having to authenticate every time
# we want PST services
ui = UserInfo()

@login_required
def gbt_schedule(request, *args, **kws):
    # serve up the GBT schedule
    timezones = ['ET', 'UTC']

    # TBF: error handling
    if request.method == 'POST': 
        timezone  = request.POST.get('tz', 'ET')
        days      = int(request.POST.get('days', 5))    
        startDate = request.POST.get('start', None) 
        startDate = datetime.strptime(startDate, '%m/%d/%Y') if startDate else datetime.now() 
    else:
        # default time range
        timezone  = 'ET'
        days      = 14 
        startDate = datetime.now()

    start = TimeAgent.truncateDt(startDate)
    end   = start + timedelta(days = days)

    # View is in ET or UTC, database is in UTC.
    pstart  = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend    = TimeAgent.est2utc(end) if timezone == 'ET' else end
    periods = Period.in_time_range(pstart, pend)

    calendar = gen_gbt_schedule(start, end, days, 'ET', periods)

    return render_to_response(
               'sesshuns/schedule.html'
             , {'calendar' : sorted(calendar.items())
              , 'day_list' : range(1, 15)
              , 'tz_list'  : timezones
              , 'timezone' : timezone
              , 'start'    : start
              , 'days'     : days
              , 'rschedule': Receiver_Schedule.extract_schedule(start, days)
              , 'timezone' : timezone})
