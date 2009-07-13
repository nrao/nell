from django      import template
from datetime    import timedelta
from sesshuns    import models

register = template.Library()

@register.filter
def hrs2sex(value):
    return str(timedelta(hours=value))[:-3]

@register.filter
def dt2sex(value):
    return str(value)[:-3]

@register.inclusion_tag('flatten.html')
def display_allotments_for_project(project_id):
    project    = models.Project.objects.get(id__exact = project_id)
    allotments = project.allotments.all()
    ids        = [a.id for a in allotments]
    return {'things': zip(ids, allotments)
          , 'label' : 'Allotment'
          , 'url'   : 'sesshuns/allotment'}
