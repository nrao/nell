from django              import template
from sesshuns            import models
from datetime            import datetime, timedelta
from sesshuns.models     import first
from sets                import Set
from utilities.TimeAgent import rad2hr, rad2deg, est2utc
from utilities           import UserInfo

register = template.Library()

# persist this object to avoid having to authenticate every time
# we want PST services
ui = UserInfo()

@register.filter
def hrs2sex(value):
    return str(timedelta(hours=value))[:-3]

@register.filter
def dt2sex(value):
    return str(value)[:-3]

@register.filter
def target_horz(value):
    t = first(value.target_set.all())
    if t is None:
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
    if t is None:
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
def get_email(user):
    return first(models.Email.objects.filter(user = user).all()).email

@register.filter
def display_name(user):
    return "%s %s" % (user.first_name, user.last_name)

@register.filter
def pretty_none(value):
    if value is None:
        return ""
    return value

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
def to_utc(date):
    return est2utc(date)

@register.filter
def get_date(format):
    return datetime.today().strftime(str(format))

@register.filter
def get_phones(user):
    # TBF: use user's credentials to get past CAS, not Mr. Nubbles!
    return "stuff"
    phones = ui.getProfileByID(user, 'dss', 'MrNubbles!')['phones']
    return ", ".join(phones)

@register.filter
def get_reservations(user):
    # TBF: use user's credentials to get past CAS, not Mr. Nubbles!
    return "stuff"
    reserves = ui.getProfileByID(user, 'dss', 'MrNubbles!')['reserves']
    reserves = [(i.strftime('%m/%d/%Y'), o.strftime('%m/%d/%Y')) for i, o in reserves]
    reserves = [i + " to " + o for i, o in reserves]
    return ", ".join(reserves)
