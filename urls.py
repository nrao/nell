from django.conf.urls.defaults     import *
from sesshuns.views                import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(''
   , url(r'^sessions/options$',   get_options)
   , url(r'^sessions$',           SessionResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^sessions/(\d+)$',     SessionResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^receivers/schedule$', receivers_schedule)
   , (r'^admin/(.*)', admin.site.root)
)
