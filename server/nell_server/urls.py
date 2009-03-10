from django.conf.urls.defaults     import *
from nell_server.sessions.views import SessionResource, PerspectiveResource

urlpatterns = patterns('',
   # ...
   url(r'^sessions$',       SessionResource(permitted_methods=('GET', 'PUT', 'POST'))),
   url(r'^sessions/(\d+)$', SessionResource(permitted_methods=('PUT', 'GET', 'POST'))),
   url(r'^sessions/perspective$', PerspectiveResource(permitted_methods=('GET', 'PUT', 'POST'))),
   url(r'^sessions/perspective/(\d+)$', PerspectiveResource(permitted_methods=('PUT', 'GET', 'POST'))),
)


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#urlpatterns = patterns('',
#    (r'^sessions/$', 'nell_server.sessions.views.index'),
#    url(r'^xml/sessions/(.*?)/?$', sessions_resource)
    # Example:
    # (r'^nell_server/', include('nell_server.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
#)
