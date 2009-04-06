from django.conf.urls.defaults     import *
from server.sesshuns.views import SessionResource, WindowResource

urlpatterns = patterns('',
   # ...
#   url(r'^sessions(/(\d+)$)?$', SessionResource(permitted_methods=('GET', 'PUT', 'POST'))),
   url(r'^sessions$',       SessionResource(permitted_methods=('GET', 'PUT', 'POST'))),
   url(r'^sessions/(\d+)$', SessionResource(permitted_methods=('PUT', 'GET', 'POST'))),
   url(r'^windows$',        WindowResource(permitted_methods=('GET', 'PUT', 'POST'))),
   url(r'^windows/(\d+)$',  WindowResource(permitted_methods=('PUT', 'GET', 'POST'))),
)
