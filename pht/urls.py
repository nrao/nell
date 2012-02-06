from django.conf.urls.defaults import patterns, include, url
from django.conf               import settings

from pht.views  import *
from pht.resources import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

authorResource   = AuthorResource()
proposalResource = ProposalResource()
sessionResource  = SessionResource()
sourceResource   = SourceResource()

urlpatterns = patterns(''
   , (r'^static/(?P<path>.*)$', 'django.views.static.serve'
    , {'document_root': settings.STATIC_PHT})
   , url(r'^$',                                  root)
   , url(r'^tree$',                              tree)
   , url(r'^proposals/([^/]+)/authors$',         authorResource.requestHandler)
   , url(r'^proposals/([^/]+)/authors/([^/]+)$', authorResource.requestHandler)
   , url(r'^proposals/([^/]+)/sources$',         proposal_sources)
   , url(r'^proposals/([^/]+)/sources/([^/]+)$', sourceResource.requestHandler)
   , url(r'^authors/([^/]+)$',                   authorResource.requestHandler)
   , url(r'^authors$',                           authorResource.requestHandler)
   , url(r'^sources/([^/]+)$',                   sourceResource.requestHandler)
   , url(r'^sources$',                           sourceResource.requestHandler)
   , url(r'^proposals/([^/]+)$',                 proposalResource.requestHandler)
   , url(r'^proposals$',                         proposalResource.requestHandler)
   , url(r'^proposal/pis',                       pis)
   , url(r'^proposal/types',                     proposal_types)
   , url(r'^proposal/observing/types',           observing_types)
   , url(r'^proposal/science/categories',        science_categories)
   , url(r'^proposal/statuses',                  statuses)
   , url(r'^pst/users',                          users)
   , url(r'^sessions/([^/]+)/sources/([^/]+)$',  session_sources)
   , url(r'^sessions/([^/]+)/sources$',          session_sources)
   , url(r'^sessions/([^/]+)/averageradec$',     session_average_ra_dec)
   , url(r'^sessions/([^/]+)$',          sessionResource.requestHandler)
   , url(r'^sessions$',                  sessionResource.requestHandler)
   , url(r'^options$',                   get_options)
   , url(r'^session/types',              session_types)
   , url(r'^weather/types',              weather_types)
   , url(r'^semesters',                  semesters)
)
