# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from datetime          import datetime
from django            import forms
from django.contrib    import admin
from django.http       import HttpResponse
from django.utils.html import escape
from users.models   import *
from scheduler.models   import *

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

def mark_as_not_contact(modeladmin, request, queryset):
    queryset.update(principal_contact = False)
mark_as_not_contact.short_description = "Unset selected as principal contact"

def mark_as_not_pi(modeladmin, request, queryset):
    queryset.update(principal_investigator = False)
mark_as_not_pi.short_description = "Unset selected as principal investigator"

def mark_as_not_observer(modeladmin, request, queryset):
    queryset.update(observer = False)
mark_as_not_observer.short_description = "Unset selected as observer"

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
    list_display = ['project_name', 'name', 'observer', 'priority', 'principal_investigator', 'principal_contact']
    list_filter = ['principal_investigator', 'principal_contact']
    search_fields = ['project__pcode', 'user__last_name', 'user__first_name']
    actions = [mark_as_contact, mark_as_observer, mark_as_pi, mark_as_not_contact, mark_as_not_observer, mark_as_not_pi]

class Observing_ParameterAdmin(admin.ModelAdmin):
    list_display = ['session', 'parameter', 'value']
    list_filter = ['parameter']

class Observing_TypeAdmin(admin.ModelAdmin):
    list_display = ['type']

#class OpportunityInline(admin.TabularInline):
#    model = Opportunity
#    extra = 1

class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']

class PeriodAdmin(admin.ModelAdmin):
    list_display = ['start', 'duration', 'session']
    actions = [mark_as_backup, mark_as_not_backup]
    ordering = ['start']
    list_filter = ['backup', 'start', 'duration', 'score']
    search_fields = ['start','session']
    date_hierarchy = 'start'

class Period_AccountingAdmin(admin.ModelAdmin):
    list_display = ['scheduled', 'not_billable', 'short_notice']

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

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'body']

class SesshunAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'grade', 'frequency', 'allotment', 'receiver_list', 'session_type', 'observing_type', 'status', 'schedulable']
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

class TargetAdmin(admin.ModelAdmin):
    search_fields = ['source']

class WindowAdmin(admin.ModelAdmin):
    def get_project_name(self):
        return self.session.project.pcode
    get_project_name.short_description = 'Project'
    get_project_name.admin_order_field = 'session__project__pcode'

    def get_session_name(self):
        return self.session.name
    get_session_name.short_description = 'Session'
    get_session_name.admin_order_field = 'session__name'

    def get_period_state(self):
        return self.default_period.state.name
    get_period_state.short_description = "Default Period's State"
    get_period_state.admin_order_field = 'default_period__state__name'

    def get_inWindow(self):
        return self.inWindow(datetime.utcnow().date())
    get_inWindow.short_description = 'In Window?'

    list_display = [get_project_name, get_session_name, 'default_period', get_period_state, get_inWindow]
    search_fields = ['session__name', 'session__project__pcode']

class UserAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'sanctioned', 'pst_id', 'original_id']
    list_filter = ['sanctioned']
    actions = [mark_as_sanctioned, mark_as_not_sanctioned]
    search_fields = ['last_name','first_name']

class Receiver_ScheduleAdmin(admin.ModelAdmin):
    search_fields = ['receiver__abbreviation','receiver__name']
    date_hierarchy = 'start_date'

class Receiver_TemperatureAdmin(admin.ModelAdmin):
    def get_receiver_name(self):
        return self.receiver.name
    get_receiver_name.short_description = 'Receiver'
    get_receiver_name.admin_order_field = 'receiver__name'
    list_display = [get_receiver_name, "frequency", "temperature"]

# Registration of Administrative Interfaces

admin.site.register(Allotment, AllotmentAdmin)
admin.site.register(Blackout)
admin.site.register(Investigator, InvestigatorAdmin)
admin.site.register(Observing_Parameter, Observing_ParameterAdmin)
admin.site.register(Observing_Type, Observing_TypeAdmin)
#admin.site.register(Opportunity)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Period_Accounting, Period_AccountingAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Project_Type, Project_TypeAdmin)
admin.site.register(Receiver, ReceiverAdmin)
#admin.site.register(Receiver_Group)
admin.site.register(Receiver_Schedule, Receiver_ScheduleAdmin)
admin.site.register(Receiver_Temperature, Receiver_TemperatureAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Sesshun, SesshunAdmin)
admin.site.register(Session_Type, Session_TypeAdmin)
#admin.site.register(Status, StatusAdmin)
admin.site.register(System)
admin.site.register(Target, TargetAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Window, WindowAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)

######################################################################
# Resource Calendar Admin Site
######################################################################

class ModelLinkWidget(forms.Widget):
    def __init__(self, obj, attrs=None):
        print "init", obj
        self.object = obj
        super(ModelLinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        print "rendering"
        if self.object.pk:
            return mark_safe(u'<a target="_blank" href="../../../%s/%s/%s/">%s</a>' % \
                                 (self.object._meta.app_label,
                                  self.object._meta.object_name.lower(),
                                  self.object.pk, self.object))
        else:
            return mark_safe(u'')


class TheForm(forms.ModelForm):
    # required=False is essential cause we don't render input tag so there will be no value submitted.
#    link = forms.CharField(label='link', required=False)

    def __init__(self, *args, **kwargs):
        super(TheForm, self).__init__(*args, **kwargs)
        # print kwargs['instance']
        # # instance is always available, it just does or doesn't have pk.
        # self.fields['link'].widget = ModelLinkWidget(self.instance)

        
class RescalAdmin(admin.sites.AdminSite):
    pass

rescal_admin = RescalAdmin(name = "rescal_admin")

class Maintenance_ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_id', 'start', 'subject', 'contacts', 'approved', 'deleted')

    fieldsets = (
        (None, {
            'fields': (('subject', '_start', 'duration', 'contacts'), 'group', 'deleted')
            }),
        ('More info', {
                'classes': ('collapse',),
                'fields': ('location', 'telescope_resource', 'software_resource',
                           'receivers', 'receiver_changes', 'other_resources', 'backends',
                           'description', 'repeat_interval', 'repeat_end', 'approvals',
                           'modifications')
                }),
    )

    readonly_fields = ('group', 'telescope_resource', 'software_resource', 'other_resources',
                       'receivers', 'backends', 'contacts', 'location', 'description',
                       'subject', 'duration', 'repeat_interval', 'repeat_end',
                       'approvals', 'modifications', 'receiver_changes', '_start')

    can_delete = False

    def group_id(self, obj):
        if obj.group:
            s = '<a href="../maintenance_activity_group/%d/">%d</a>' % \
                (obj.group_id, obj.group_id)
        else:
            s = '-'
        return s

    group_id.allow_tags = True
    group_id.admin_order_field = "maintenance_activity.group_id"


    def start(self, obj):
        return obj.get_start()

    start.admin_order_field = "maintenance_activity._start"




class Maintenance_ActivityInline(admin.TabularInline):
    model = Maintenance_Activity
    fields = ('_start', 'subject', 'contacts', 'approved', 'deleted')
    readonly_fields = ('_start', 'subject', 'contacts', 'approved')
    # these objects can be soft-deleted by setting a 'deleted' filed.
    # if 'can_delete' is true, they can also be hard deleted, which
    # may be confusing.  Disable.
    can_delete = False
    # Use a slightly custom template, because the default one insists
    # on printing the __unicode__() output of the object on its own
    # line on the table, despite the profided fields above.
    template = 'users/admin/edit_inline/tabular.html'
    extra = 0
    form = TheForm


class Maintenance_Activity_GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'period_id', 'week_of', 'rank', 'summary', 'deleted')

    fieldsets = (
        (None, {
            'fields': ('period', 'week', 'rank', 'deleted')
            }),
    )

    readonly_fields = ('period', 'rank', 'week')
    can_delete = False
    inlines = [Maintenance_ActivityInline,]

    def period_id(self, obj):
        if obj.period:
            return obj.period.id
        else:
            return '-'

    period_id.admin_order_field = "maintenance_activity_group.period_id"

    def week_of(self, obj):
        return obj.get_week().date()

    week_of.admin_order_field = "maintenance_activity_group.week"

    def summary(self, obj):
        l = obj.__unicode__().split(';')[4]
        max_len = 100

        if len(l) > max_len:
            l = l[0:max_len - 1] + "..."

        return l

rescal_admin.register(Maintenance_Activity, Maintenance_ActivityAdmin)
rescal_admin.register(Maintenance_Activity_Group, Maintenance_Activity_GroupAdmin)
