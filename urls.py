from django.conf.urls.defaults     import *
from django.conf                   import settings
from sesshuns.views                import *
from sesshuns.resources            import *
from sesshuns.observers            import *
from sesshuns.operators            import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Note a blank comment attached to the url denotes local access only

urlpatterns = patterns(''
   , url(r'^profile/(\d+)/blackout$',                      blackout)
   , url(r'^profile/(\d+)/blackout/form$',                 blackout_form)
   , url(r'^profile/(\d+)/dynamic_contact/form$',          dynamic_contact_form)
   , url(r'^profile/(\d+)/dynamic_contact$',               dynamic_contact_save)
   , url(r'^profile/(\d+)$',                               profile)
   , url(r'^profile',                                      profile)
   , url(r'^$',                                            home)
   , url(r'^project/([^/]+)/events$',                      events)
   , url(r'^project/([^/]+)/unavailable$',                 dates_not_schedulable)
   , url(r'^project/([^/]+)$',                             project)
   , url(r'^project/([^/]+)/notes/form$',                  project_notes_form)
   , url(r'^project/([^/]+)/notes$',                       project_notes_save)
   , url(r'^project/([^/]+)/schedulers_notes/form$',       project_snotes_form)
   , url(r'^project/([^/]+)/schedulers_notes$',            project_snotes_save)
   , url(r'^project/([^/]+)/investigator/(\d+)/observer$', toggle_observer)
   , url(r'^project/([^/]+)/investigator/(\d+)/priority/([^/]+)$', modify_priority)
   , url(r'^project/([^/]+)/session/([^/]+)/enable$',      toggle_session)
   , url(r'^projects$',           ProjectResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^projects/(\d+)$',     ProjectResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , url(r'^projects/ical$',      get_ical)
   , url(r'^projects/time_accounting/([^/]+)$',              time_accounting)
   , url(r'^schedule/$',                                   gbt_schedule)
   , url(r'^schedule/public$',                             public_schedule)
   , url(r'^schedule/email$',                              scheduling_email)
   , url(r'^search$',                                      search)
   , url(r'^sessions/options$',   get_options) #
   , url(r'^sessions/time_accounting/([^/]+)$',   session_time_accounting) #
   , url(r'^schedule/change_schedule$', change_schedule) #
   , url(r'^schedule/shift_period_boundaries$', shift_period_boundaries) #
   , url(r'^sessions$',           SessionResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^sessions/(\d+)$',     SessionResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , url(r'^receivers$',          rcvr_schedule) #
   , url(r'^receivers/schedule$', receivers_schedule) #
   , url(r'^receivers/change_schedule$', change_rcvr_schedule) #
   , url(r'^receivers/shift_date$', shift_rcvr_schedule_date) #
   , url(r'^period/([^/]+)/moc_reschedule$', moc_reschedule)
   , url(r'^period/([^/]+)/moc_degraded$', moc_degraded)
   , url(r'^period/([^/]+)/time_accounting$', period_time_accounting) #
   , url(r'^periods/publish',     publish_periods) #
   , url(r'^periods/delete_pending', delete_pending) #
 
   , url(r'^periods/(UTC)$',      PeriodResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^periods/(ET)$',       PeriodResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^periods/(UTC)/(\d+)$',PeriodResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , url(r'^periods/(ET)/(\d+)$', PeriodResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , url(r'^windows$',           WindowResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^windows/(\d+)$',     WindowResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , (r'^admin/',                 include(admin.site.urls)) #
   , (r'^accounts/login/$', 'django_cas.views.login') #
   , (r'^accounts/logout/$', 'django_cas.views.logout')
   , (r'^robots.txt$', 'django.views.static.serve',
        { 'path'         : "txt/robots.txt"
        , 'document_root': settings.STATIC_DOC_ROOT
        , 'show_indexes' : False})
   , (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT})
)
