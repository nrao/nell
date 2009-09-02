from django.contrib    import admin
from django.http       import HttpResponse
from django.utils.html import escape
from sesshuns.models   import * 

# Inlines

class Observing_ParameterInline(admin.TabularInline):    
    model = Observing_Parameter
    extra = 1

class PeriodInline(admin.TabularInline):
    model = Period
    extra = 1

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class Receiver_GroupInline(admin.StackedInline):
    model = Receiver_Group
    extra = 1

class SesshunInline(admin.TabularInline):
    model = Sesshun
    extra = 1

class TargetInline(admin.TabularInline):
    model = Target
    extra = 1

class WindowInline(admin.TabularInline):
    model = Window
    extra = 1

# Actions for Investigators

def mark_as_contact(modeladmin, request, queryset):
    queryset.update(principal_contact = True)
mark_as_contact.short_description = "Set selected as principal contact"

def mark_as_pi(modeladmin, request, queryset):
    queryset.update(principal_investigator = True)
mark_as_pi.short_description = "Set selected as principal investigator"

def mark_as_observer(modeladmin, request, queryset):
    queryset.update(observer = True)
mark_as_observer.short_description = "Set selected as observer"

def mark_as_friend(modeladmin, request, queryset):
    queryset.update(friend = True)
mark_as_friend.short_description = "Set selected as friend"

def mark_as_not_contact(modeladmin, request, queryset):
    queryset.update(principal_contact = False)
mark_as_not_contact.short_description = "Unset selected as principal contact"

def mark_as_not_pi(modeladmin, request, queryset):
    queryset.update(principal_investigator = False)
mark_as_not_pi.short_description = "Unset selected as principal investigator"

def mark_as_not_observer(modeladmin, request, queryset):
    queryset.update(observer = False)
mark_as_not_observer.short_description = "Unset selected as observer"

def mark_as_not_friend(modeladmin, request, queryset):
    queryset.update(friend = False)
mark_as_not_friend.short_description = "Unset selected as friend"

# Actions for Periods

def mark_as_backup(modeladmin, request, queryset):
    queryset.update(backup = True)
mark_as_backup.short_description = "Mark selected periods as being backup"

def mark_as_not_backup(modeladmin, request, queryset):
    queryset.update(backup = False)
mark_as_not_backup.short_description = "Mark selected periods as not being backup"

# Actions for Projects

def mark_as_not_completed(modeladmin, request, queryset):
    queryset.update(complete = False)
mark_as_not_completed.short_description = "Mark selected projects as not complete"

def mark_as_completed(modeladmin, request, queryset):
    queryset.update(complete = True)
mark_as_completed.short_description = "Mark selected projects as complete"

# Actions for Users
def mark_as_sanctioned(modeladmin, request, queryset):
    queryset.update(sanctioned = True)
mark_as_sanctioned.short_description = "Sanction"

def mark_as_not_sanctioned(modeladmin, request, queryset):
    queryset.update(sanctioned = False)
mark_as_not_sanctioned.short_description = "Un-sanction"

# Administrative Interfaces

class AllotmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'psc_time', 'total_time', 'max_semester_time', 'grade']

    def response_change(self, request, obj):
        if request.POST.has_key('_popup'):
            # Get rid of pop-ups and refresh parent.
            return HttpResponse('<script type="text/javascript">window.opener.location.href = window.opener.location.href; window.close();</script>')
        return admin.ModelAdmin.response_change(self, request, obj)

class InvestigatorAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'name', 'observer', 'priority', 'friend', 'principal_investigator', 'principal_contact']
    list_filter = ['principal_investigator', 'principal_contact']
    search_fields = ['project__pcode', 'user__last_name', 'user__first_name']
    actions = [mark_as_contact, mark_as_observer, mark_as_pi, mark_as_friend, mark_as_not_contact, mark_as_not_observer, mark_as_not_pi, mark_as_not_friend]

class Observing_ParameterAdmin(admin.ModelAdmin):
    list_display = ['session', 'parameter', 'value']
    list_filter = ['parameter']

class Observing_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

class OpportunityInline(admin.TabularInline):
    model = Opportunity
    extra = 1

class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']

class PeriodAdmin(admin.ModelAdmin):
    list_display = ['start', 'duration', 'session']
    actions = [mark_as_backup, mark_as_not_backup]
    ordering = ['start']
    list_filter = ['backup', 'start', 'duration', 'score']
    search_fields = ['start','session']
    date_hierarchy = 'start'

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['pcode', 'name', 'semester', 'project_type', 'principal_contact', 'thesis', 'complete', 'start_date', 'end_date']
    actions = [mark_as_completed, mark_as_not_completed]
    ordering = ['pcode']
    list_filter = ['semester', 'project_type', 'complete', 'thesis']
    search_fields = ['pcode']
    date_hierarchy = 'start_date'
    inlines = [SesshunInline]

class Project_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']
    display = 'type'

class ReceiverAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'freq_low', 'freq_hi']

class SemesterAdmin(admin.ModelAdmin):
    list_display = ['semester']

class SesshunAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'letter_grade', 'frequency', 'allotment', 'receiver_list', 'session_type', 'observing_type', 'status', 'schedulable']
    list_filter = ['session_type', 'observing_type', 'frequency']
    search_fields = ['name']
    exclude = ('allotment',)
    inlines = [Receiver_GroupInline
             , TargetInline
             , Observing_ParameterInline
             , PeriodInline
             , WindowInline]

class Session_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

class StatusAdmin(admin.ModelAdmin):
    search_fields = ['id'] 

class WindowAdmin(admin.ModelAdmin):
    inlines = [OpportunityInline]

class UserAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'sanctioned', 'pst_id', 'original_id']
    list_filter = ['sanctioned']
    actions = [mark_as_sanctioned, mark_as_not_sanctioned]
    search_fields = ['last_name','first_name']

# Registration of Administrative Interfaces

admin.site.register(Allotment, AllotmentAdmin)
admin.site.register(Blackout)
admin.site.register(Investigator, InvestigatorAdmin)
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
admin.site.register(User, UserAdmin)
admin.site.register(Window, WindowAdmin)
