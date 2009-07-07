from django      import template
from datetime    import timedelta

register = template.Library()

@register.filter
def hrs2sex(value):
    return str(timedelta(hours=value))[:-3]

@register.filter
def dt2sex(value):
    return str(value)[:-3]
