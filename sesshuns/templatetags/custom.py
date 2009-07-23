from django      import template
from datetime    import timedelta

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
        if abs(mins - 60) < 0.1:
            mins = 0.0
            horz = int(horz) + 1
        secs = 0.0
    return ":".join(map(str, [int(horz), int(mins), "%.1f" % secs]))

@register.filter
def target_vert(value):
    t = first(value.target_set.all())
    if t is None:
        return ""
    return "%.3f" % rad2deg(t.vertical)

@register.filter
def display_name(user):
    return "%s %s" % (user.first_name, user.last_name)
