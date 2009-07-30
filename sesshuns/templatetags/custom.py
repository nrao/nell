from django      import template
from datetime    import timedelta
from sesshuns    import models

from sesshuns.models     import first
from utilities.TimeAgent import rad2hr, rad2deg

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
def display_name(user):
    return "%s %s" % (user.first_name, user.last_name)

@register.filter
def pretty_none(value):
    if value is None:
        return ""
    return value
