# -*- coding: iso-8859-15 -*-

from django                  import template
from django.utils.safestring import SafeUnicode
from sesshuns                import models
from datetime                import datetime, timedelta
from sesshuns.models         import first
from sets                    import Set
from nell.tools              import TimeAccounting
from nell.utilities          import TimeAgent
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException

register = template.Library()

@register.filter
def multipleRowWindow(window):
    return not window["contigious"] or len(window["periods"]) > 0

@register.filter
def hrs2sex(value):
    if isinstance(value, str):
        return value
    else:
        return str(timedelta(hours=value))[:-3]

@register.filter
def dt2sex(value):
    return str(value)[:-3]

@register.filter
def target_horz(value):
    t = first(value.target_set.all())
    tag = "*" if t.isEphemeris() else ""
    return t.get_horizontal() + tag

@register.filter
def target_vert(value):
    t = first(value.target_set.all())
    tag = "*"  if t.isEphemeris() else ""
    return t.get_vertical() + tag

@register.inclusion_tag('flatten.html')
def edit_allotment(sesshun_id):
    session   = models.Sesshun.objects.get(id__exact = sesshun_id)
    allotment = session.allotment
    return {
        'things'   : [(allotment.id, allotment)]
      , 'label'    : 'Allotment'
      , 'edit_only': True
      , 'base_url' : models.Allotment.base_url
    }

@register.inclusion_tag('flatten.html')
def display_allotments_for_project(project_id):
    project    = models.Project.objects.get(id__exact = project_id)
    allotments = project.allotments.all()
    ids        = [a.id for a in allotments]

    return {
        'things'   : zip(ids, allotments)
      , 'label'    : 'Allotment'
      , 'edit_only': False
      , 'base_url' : models.Allotment.base_url
    }

@register.filter
def getTimeBilled(obj):
    return TimeAccounting().getTime("time_billed", obj)

@register.filter
def getSumTotalTime(project):
    return TimeAccounting().getProjectTotalTime(project)

@register.filter
def has_lost_time(period):
    return period.accounting.lost_time() > 0.

@register.filter
def get_lost_time(period):
    lt = []
    if period.accounting.lost_time_weather > 0:
        lt.append("weather = %2.2f hr" % period.accounting.lost_time_weather)
    if period.accounting.lost_time_rfi > 0:
        lt.append("RFI = %2.2f hr" % period.accounting.lost_time_rfi)
    if period.accounting.lost_time_other > 0:
        lt.append("other = %2.2f hr" % period.accounting.lost_time_other)

    return ", ".join(lt)

@register.filter
def get_email(user):
    emails = user.getStaticContactInfo()['emails']
    return emails[0] if emails else ""

@register.filter
def display_name(user):
    return "%s %s" % (user.first_name, user.last_name)

@register.filter
def pretty_none(value):
    return value if value else ""

@register.filter
def project_type(project):
    # types: 'A', 'M', 'T', 'C'
    if project.project_type.type == 'science':
        type = 'A'
    else:
        if project.is_maintenance():
            type = 'M'
        elif project.is_commissioning():
            type = 'C'
        elif project.is_calibration():
            type = 'K'
        else:
            type = 'T'
    return type

@register.filter
def get_projects(user):
    return sorted([i.project for i in user.investigator_set.all()]
                , lambda x, y: cmp(x.pcode, y.pcode))

@register.filter
def sort_projects(projects):
    return sorted(projects, lambda x, y: cmp(x.pcode, y.pcode))

@register.filter
def get_receiver_change(schedule, day):
    if day.date() not in [d.date() for d in schedule.keys()]:
        return "- No receiver changes" # No receiver change today

    date     = [d for d in schedule.keys() if d.date() == day.date()][0]
    prevdate = [d for d in sorted(schedule.keys()) if d < date][-1]
    added    = [r.abbreviation
                for r in (Set(schedule[date]) - Set(schedule[prevdate]))]
    removed  = [r.abbreviation
                for r in (Set(schedule[prevdate]) - Set(schedule[date]))]

    string  = "Add: " + ", ".join(added) + " " if added else ""
    string += ", " if string else ""
    string += "Remove: " + ", ".join(removed) if removed else ""

    return "- " + string if string else "- No receiver changes"

@register.filter
def end_date(start_date, days):
    retval = start_date + timedelta(days = days -1)
    return retval.strftime("%Y-%m-%d")

@register.filter
def date_no_secs(value):
    if isinstance(value, str):
        return value
    else:
        return value.strftime("%Y-%m-%d %H:%M")

@register.filter
def get_receivers(schedule, day):
    date = [d for d in sorted(schedule.keys()) if d.date() <= day.date()][-1]
    rcvrs = schedule[date] if date else []
    return ", ".join([r.abbreviation for r in rcvrs])

@register.filter
def get_utc_offset(date):
    o = date.utcoffset()
    return -1 * (o.days * 24 * 3600 + o.seconds) / 3600

@register.filter
def to_utc(date):
    return est2utc(date)

@register.filter
def get_date(format):
    return datetime.today().strftime(str(format))

@register.filter
def get_cal_start(calendar):
    return calendar[0][0]

@register.filter
def get_cal_end(calendar):
    return calendar[-1][0]

@register.filter
def format_list(aList):
    "Makes a list a string"
    return ", ".join(aList) if aList else "None"

@register.filter
def get_duration(start, end):
    return "%.2f" % ((end - start).seconds / 3600.) # hours

@register.filter
def format_reservations(reservations):
    return ", ".join([a + " to " + b for a, b in [(x.strftime('%m-%d-%Y'), y.strftime('%m-%d-%Y')) for x, y in reservations]]) if reservations else "None"

@register.filter
def moc_class(moc_met):
    return "" if moc_met else "moc_failure"

@register.filter
def moc_reschedule(period):
    "Popups are issued when start <= 30 minutes if moc is False."
    diff = period.start - datetime.utcnow()
    if not period.moc_ack and \
       diff >  timedelta(seconds = 0) and \
       diff <= timedelta(minutes = 30):
        return not period.moc_met()
    else:
        return False

@register.filter
def moc_degraded(period):
    "Popups are issued when a period has started and if moc is False."
    now = datetime.utcnow()
    if not period.moc_ack and \
       now > period.start and now < period.end():
        return not period.moc_met()
    else:
        return False

@register.filter
def split_over_two_table_columns(value, splitter):
    """
    Used by the resource calendar to split a bunch of HTML controls
    that are separated by a '<br>' over two table columns.
    """
    a = value.split('<br>')
    a.insert(len(a)/2 + len(a) % 2, splitter)
    value = SafeUnicode('<br>'.join(a))
    return value
split_over_two_table_columns.is_safe = True


@register.filter
def flag_rc_conflicts(ma, mas):
    """
    Used to flag the summary of a maintenance activity for conflicts.
    Conflicting resources will be output in red.  Resources will be
    flagged as conflicting if any other activity uses the same
    mutually exclusive resource during some overlapping time,
    regardless of who caused the conflict.
    """
    # this will check against all other activities in group to see if
    # any resources are in conflict.  A list of resource abbreviations
    # will be returned, over which the filter will iterate.
    
    conflicts = ma.check_for_conflicting_resources(mas)
    summary = ma.summary()

    for i in conflicts:
        rpos = summary.find(i)

        if rpos != -1:
            summary = summary.replace(i, i[:2] + '<font color="red">' + i[2:] + '</font>', 1)

    summary = SafeUnicode(summary)
    return summary
flag_rc_conflicts.is_safe = True

@register.filter
def get_first_start(mas, tz):
    if tz == "ET":
        r = TimeAgent.utc2est(mas[0].get_start())
    else:
        r = mas[0].get_start()
    return r

@register.filter
def get_last_end(mas, tz):
    if tz == "ET":
        r = TimeAgent.utc2est(mas[-1].get_end())
    else:
        r = mas[-1].get_end()
    return r

@register.filter
def day_of_week(date, dow):
    return date.weekday() == dow


@register.filter
def floating_maint_periods(day):
    """
    Takes the day (assumes it is Monday) and finds the maintenance
    periods for that week.  Returns a string representing the
    *pending* periods for that week.  Period 1 is 'A', Period 2 is
    'B', Period 3 (if it exists) is 'C' etc.  Thus, assuming two
    maintenance periods, if 1 is fixed and 2 is pending, returns 'B'.
    If both are pending, returns 'AB'. etc.  Works for however many
    periods exist for that week.
    """

    pend = []

    try:
        delta = timedelta(days = 7)
        mp = models.Period.objects\
            .filter(session__project__pcode = "Maintenance")\
            .filter(start__gte = day)\
            .filter(start__lt = day + delta)\
            .order_by('start')

        for i in range(0, len(mp)):
            if mp[i].isPending():
                mas = models.Maintenance_Activity.get_maintenance_activity_set(mp[i])
                pend.append((chr(i + 65),  # 65 is ASCII 'A'
                             TimeAgent.utc2est(mp[i].start),
                             TimeAgent.utc2est(mp[i].end()),
                             mp[i],
                             mas))

    except:
        printException(formatExceptionInfo())
        pend = []

    return pend
