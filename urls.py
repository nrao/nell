from django.conf.urls.defaults     import *
from django.conf                   import settings
from sesshuns.views                import *
from sesshuns.resources            import *
from sesshuns.observers            import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Note a blank comment attached to the url denotes local access only

urlpatterns = patterns(''
   , url(r'^schedule$',                                    schedule)
   , url(r'^search$',                                      search)
   , url(r'^profile/(\d+)/blackout$',                      blackout)
   , url(r'^profile/(\d+)/blackout/form$',                 blackout_form)
   , url(r'^profile/(\d+)/dynamic_contact/form$',          dynamic_contact_form)
   , url(r'^profile/(\d+)/dynamic_contact$',               dynamic_contact_save)
   , url(r'^profile/(\d+)$',                               profile)
   , url(r'^profile',                                      profile)
   , url(r'^$',                                            profile)
   , url(r'^project/([^/]+)/events$',                      events)
   , url(r'^project/([^/]+)/unavailable$',                 dates_not_schedulable)
   , url(r'^project/([^/]+)$',                             project)
   , url(r'^project/([^/]+)/investigator/(\d+)/observer$', toggle_observer)
   , url(r'^project/([^/]+)/investigator/(\d+)/priority/([^/]+)$', modify_priority)
   , url(r'^project/([^/]+)/session/([^/]+)/enable$',      toggle_session)
   , url(r'^projects$',           ProjectResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^projects/(\d+)$',     ProjectResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , url(r'^projects/ical$',      get_ical)
   , url(r'^sessions/options$',   get_options) #
   , url(r'^sessions$',           SessionResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^sessions/(\d+)$',     SessionResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , url(r'^receivers/schedule$', receivers_schedule) #
   , url(r'^periods$',            PeriodResource(permitted_methods=('GET', 'PUT', 'POST'))) #
   , url(r'^periods/(\d+)$',      PeriodResource(permitted_methods=('PUT', 'GET', 'POST'))) #
   , (r'^admin/',                 include(admin.site.urls)) #
   , (r'^accounts/login/$', 'django_cas.views.login')
   , (r'^accounts/logout/$', 'django_cas.views.logout')
   , (r'^robots.txt$', 'django.views.static.serve',
        { 'path'         : "txt/robots.txt"
        , 'document_root': settings.STATIC_DOC_ROOT
        , 'show_indexes' : False})
   , (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT})
)
