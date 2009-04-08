from server.sesshuns.models import Sesshun, Semester, Project_Type, Allotment, Project, Session_Type, Observing_Type, Receiver, Parameter
from django.contrib import admin

class SesshunAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'frequency', 'allotment']
    list_filter = ['name',  'project']
    search_fields = ['name']
    #date_hierarchy = 'pub_date'

class SesshunInline(admin.TabularInline):
    model = Sesshun
    extra = 1

class SemesterAdmin(admin.ModelAdmin):
    list_display = ['semester']

class Project_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']
    display = 'type'

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'pcode', 'semester', 'project_type']
    inlines = [SesshunInline]

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class AllotmentAdmin(admin.ModelAdmin):
    list_display = ['psc_time', 'total_time', 'max_semester_time']
    inlines = [SesshunInline]

class Session_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

class Observing_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

class ReceiverAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'freq_low', 'freq_hi']

class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']

admin.site.register(Sesshun, SesshunAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Project_Type, Project_TypeAdmin)
admin.site.register(Allotment, AllotmentAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Session_Type, Session_TypeAdmin)
admin.site.register(Observing_Type, Observing_TypeAdmin)
admin.site.register(Receiver, ReceiverAdmin)
admin.site.register(Parameter, ParameterAdmin)

