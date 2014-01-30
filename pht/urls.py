from django.conf.urls.defaults import patterns, include, url
from django.conf               import settings
from django.contrib.auth.decorators import login_required

from pht.views  import *
from pht.resources import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

authorResource    = AuthorResource()
periodResource    = PeriodResource()
dssPeriodResource = DssPeriodResource()
proposalResource  = ProposalResource()
sessionResource   = SessionResource()
sourceResource    = SourceResource()

urlpatterns = patterns(''
   , (r'^static/(?P<path>.*)$', 'django.views.static.serve'
    , {'document_root': settings.STATIC_PHT})
   , url(r'^notify$',                            notify)
   , url(r'^$',                                  root)
   , url(r'^reports/proposalworksheet$',         proposal_worksheet)
   , url(r'^reports/proposalsummary$',           proposal_summary)
   , url(r'^reports/otherproposalsummary$',      other_proposal_summary)
   , url(r'^reports/jointproposalsummary$',      joint_proposal_summary)
   , url(r'^reports/proposalranking$',           proposal_ranking)
   , url(r'^reports/proposalranking/export$',    proposal_ranking_export)
   , url(r'^reports/semester_summary$',          semester_summary)
   , url(r'^reports/sponsoredproposals$',        sponsored_proposals)
   , url(r'^reports/lst_pressures$',             lst_pressure_report)
   , url(r'^sources/export$',                    sources_export)
   , url(r'^sources/import$',                    sources_import)
   , url(r'^sources/transfer$',                  sources_transfer)
   , url(r'^tree$',                              tree)
   , url(r'^calendar/lstrange$',                 lst_range)
   , url(r'^import$',                            import_proposals)
   , url(r'^import/semester$',                   import_semester)
   , url(r'^import/pst$',                        import_pst_proposals)
   , url(r'^export$',                            export_proposals)
   , url(r'^export/semester$',                   export_semester)
   , url(r'^proposals/export$',                  proposals_export)
   , url(r'^proposals/([^/]+)/authors$',         login_required(authorResource.requestHandler))
   , url(r'^proposals/([^/]+)/authors/([^/]+)$', login_required(authorResource.requestHandler))
   , url(r'^proposals/([^/]+)/sources$',         proposal_sources)
   , url(r'^proposals/([^/]+)/sources/([^/]+)$', login_required(sourceResource.requestHandler))
   , url(r'^authors/([^/]+)$',                   login_required(authorResource.requestHandler))
   , url(r'^authors$',                           login_required(authorResource.requestHandler))
   , url(r'^sources/([^/]+)$',                   login_required(sourceResource.requestHandler))
   , url(r'^sources$',                           login_required(sourceResource.requestHandler))
   , url(r'^proposals/([^/]+)$',                 login_required(proposalResource.requestHandler))
   , url(r'^proposals$',                         login_required(proposalResource.requestHandler))
   , url(r'^proposal/pis',                       pis)
   , url(r'^proposal/types',                     proposal_types)
   , url(r'^proposal/observing/types',           observing_types)
   , url(r'^proposal/science/categories',        science_categories)
   , url(r'^proposal/statuses',                  statuses)
   , url(r'^pst/users',                          users)
   , url(r'^pst/user/info$',                     user_info)
   , url(r'^pst/pcodes$',                        pst_proposal_codes)
   , url(r'^sessions/export$',                   sessions_export)
   , url(r'^sessions/([^/]+)/sources/([^/]+)$',  session_sources)
   , url(r'^sessions/([^/]+)/sources$',          session_sources)
   , url(r'^sessions/([^/]+)/averageradec$',     session_average_ra_dec)
   , url(r'^sessions/([^/]+)/calculateLSTs$',    session_calculate_LSTs)
   , url(r'^sessions/([^/]+)/generatePeriods$',  session_generate_periods)
   , url(r'^sessions/([^/]+)$',          login_required(sessionResource.requestHandler))
   , url(r'^sessions$',                  login_required(sessionResource.requestHandler))
   , url(r'^options$',                   get_options)
   , url(r'^proposal_timeline$',         proposal_timeline)
   , url(r'^nrao_pht_pressure$',              nrao_pht_pressure)
   , url(r'^lst_pressure$',              lst_pressure)
   , url(r'^lst_pressure/print/([^/]+)$', print_lst_pressure)
   , url(r'^session/grades',             session_grades)
   , url(r'^session/observing/types',    session_observing_types)
   , url(r'^session/types',              session_types)
   , url(r'^session/separations',        session_separations)
   , url(r'^periods/([^/]+)$',                 login_required(periodResource.requestHandler))
   , url(r'^periods$',                         login_required(periodResource.requestHandler))
   , url(r'^dss/periods/([^/]+)/([^/]+)$',     login_required(dssPeriodResource.requestHandler))
   , url(r'^dss/periods/([^/]+)$',             login_required(dssPeriodResource.requestHandler))
   , url(r'^weather/types',              weather_types)
   , url(r'^semesters',                  semesters)
   , url(r'^receivers',                  receivers)
   , url(r'^backends',                   backends)
   , url(r'^friends',                    friends)
   , url(r'^sponsors',                   sponsors)
   , url(r'^import_reports',             import_reports)
   , url(r'^source/epochs',              source_epochs)
   , url(r'^source/systems',             source_systems)
   , url(r'^source/velocity_types',      source_velocity_types)
   , url(r'^source/conventions',         source_conventions)
   , url(r'^source/reference_frames',    source_reference_frames)
)
