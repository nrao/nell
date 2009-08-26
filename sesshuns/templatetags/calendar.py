from django   import template
from datetime import date, timedelta

register = template.Library()
OFFSET   = 14

@register.filter
def get_day(n):
    'Find the n_th day on the calendar.'
    today = date.today() # TBF:  Get this from the view.
    start = today - timedelta(today.isoweekday())
    return start + timedelta(n)

@register.filter
def get_label(w, d):
    'Certain day labels should include month names.'
    n      = 7 * w + d
    day    = get_day(n)
    format = '%b %d' if day.day == 1 or n == 0 else '%d'
    return day.strftime(format)

def get_current_month(n):
    day   = get_day(7*(n/7))
    pivot = day if day.day == 1 else day + timedelta(7)
    return pivot.month

@register.filter
def get_color(w, d):
    n   = 7 * w + d
    day = get_day(n)
    return 'black' if day.month == get_current_month(n) else '#888888'

@register.filter
def get_bgcolor(w, d):
    day = get_day(7 * w + d)
    return '#EEEEEE' if day == date.today() else '#FFFFFF'

@register.filter
def get_next(today):
    dt = today + timedelta(days = OFFSET)
    return "%s/%s/%s/" % (dt.year, dt.month, dt.day)

@register.filter
def get_previous(today):
    dt = today - timedelta(days = OFFSET)
    return "%s/%s/%s/" % (dt.year, dt.month, dt.day)
