from django              import template
from sesshuns            import models
from datetime            import datetime, timedelta
from sesshuns.models     import first
from sets                import Set
from utilities.TimeAgent import rad2hr, rad2deg, est2utc

register = template.Library()

@register.filter
def hrs2sex(value):
    return str(timedelta(hours=value))[:-3]

@register.filter
def dt2sex(value):
    return str(value)[:-3]

@register.filter
def target_horz(value):
    t = first(value.target_set.all())
    if t is None or t.horizontal is None:
        return ""
    horz = rad2hr(t.horizontal)
    mins = (horz - int(horz)) * 60
    secs = (mins - int(mins)) * 60
    if abs(secs - 60.) < 0.1:
        mins = int(mins) + 1
        if abs(mins - 60.) < 0.1:
            mins = 0.0
            horz = int(horz) + 1
        secs = 0.0
    return ":".join(map(str, [int(horz), int(mins), "%.1f" % secs]))

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

@register.filter
def target_vert(value):
    t = first(value.target_set.all())
    if t is None or t.vertical is None:
        return ""
    return "%.3f" % rad2deg(t.vertical)

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
    # types: 'A', 'M', 'T'
    if project.project_type.type == 'science':
        type = 'A'
    else:
        if project.name == 'Maintenance':
            type = 'M'
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
def format_reservations(reservations):
    return ", ".join([a + " to " + b for a, b in [(x.strftime('%m-%d-%Y'), y.strftime('%m-%d-%Y')) for x, y in reservations]]) if reservations else "None"

@register.filter
def moc_class(period):
    return "" if period.moc_met() else "moc_failure"

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
