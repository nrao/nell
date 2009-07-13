from django.contrib  import admin
from sesshuns.models import * 

class Receiver_GroupInline(admin.TabularInline):
    model = Receiver_Group
    extra = 1

class WindowInline(admin.TabularInline):
    model = Window
    extra = 1

class TargetInline(admin.TabularInline):
    model = Target
    extra = 1

class PeriodInline(admin.TabularInline):
    model = Period
    extra = 1

class Observing_ParameterInline(admin.TabularInline):    
    model = Observing_Parameter
    extra = 1

class SesshunAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'letter_grade', 'frequency', 'allotment', 'receiver_list', 'session_type', 'observing_type', 'status', 'schedulable']
    list_filter = ['session_type', 'observing_type', 'frequency']
    search_fields = ['name']
    inlines = [Receiver_GroupInline
             , TargetInline
             , Observing_ParameterInline
             , PeriodInline
             , WindowInline]

class SesshunInline(admin.TabularInline):
    model = Sesshun
    extra = 1

class SemesterAdmin(admin.ModelAdmin):
    list_display = ['semester']

def mark_as_backup(modeladmin, request, queryset):
    queryset.update(backup = True)
mark_as_backup.short_description = "Mark selected periods as being backup"

def mark_as_not_backup(modeladmin, request, queryset):
    queryset.update(backup = False)
mark_as_not_backup.short_description = "Mark selected periods as not being backup"

class PeriodAdmin(admin.ModelAdmin):
    list_display = ['start', 'duration', 'session']
    actions = [mark_as_backup, mark_as_not_backup]
    ordering = ['start']
    list_filter = ['backup', 'start', 'duration', 'score']
    search_fields = ['start','session']
    date_hierarchy = 'start'

class Project_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']
    display = 'type'

def ignore_grade(modeladmin, request, queryset):
    queryset.update(ignore_grade = True)
ignore_grade.short_description = "Ignore grade on selected projects"

def do_not_ignore_grade(modeladmin, request, queryset):
    queryset.update(ignore_grade = False)
do_not_ignore_grade.short_description = "Do not ignore grade on selected projects"

def mark_as_not_completed(modeladmin, request, queryset):
    queryset.update(complete = False)
mark_as_not_completed.short_description = "Mark selected projects as not complete"

def mark_as_completed(modeladmin, request, queryset):
    queryset.update(complete = True)
mark_as_completed.short_description = "Mark selected projects as complete"

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['pcode', 'name', 'semester', 'project_type', 'principal_contact', 'thesis', 'ignore_grade', 'complete', 'start_date', 'end_date']
    actions = [mark_as_completed, mark_as_not_completed, ignore_grade, do_not_ignore_grade]
    ordering = ['pcode']
    list_filter = ['semester', 'project_type', 'complete', 'thesis', 'ignore_grade']
    search_fields = ['pcode']
    date_hierarchy = 'start_date'
    inlines = [SesshunInline]

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class AllotmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'psc_time', 'total_time', 'max_semester_time', 'grade']
    inlines      = [SesshunInline]

class Session_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

class Observing_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

class ReceiverAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'freq_low', 'freq_hi']

class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']

class Observing_ParameterAdmin(admin.ModelAdmin):
    list_display = ['session', 'parameter', 'value']
    list_filter = ['parameter']

class StatusAdmin(admin.ModelAdmin):
    search_fields = ['id'] 

class OpportunityInline(admin.TabularInline):
    model = Opportunity
    extra = 1

class WindowAdmin(admin.ModelAdmin):
    inlines = [OpportunityInline]

admin.site.register(Allotment, AllotmentAdmin)
admin.site.register(Blackout)
admin.site.register(Observing_Parameter, Observing_ParameterAdmin)
admin.site.register(Observing_Type, Observing_TypeAdmin)
admin.site.register(Opportunity)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Project_Type, Project_TypeAdmin)
admin.site.register(Receiver, ReceiverAdmin)
#admin.site.register(Receiver_Group)
admin.site.register(Receiver_Schedule)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Sesshun, SesshunAdmin)
admin.site.register(Session_Type, Session_TypeAdmin)
#admin.site.register(Status, StatusAdmin)
admin.site.register(System)
admin.site.register(Target)
admin.site.register(Window, WindowAdmin)
