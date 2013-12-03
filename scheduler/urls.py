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

from django.conf.urls.defaults import *

from scheduler.views     import *
from scheduler.resources import *

urlpatterns = patterns(''
   , url(r'^currentobs$',                                  current_obs_xml) 
   , url(r'^configurations/explorer/columnConfigs$',       column_configurations_explorer)
   , url(r'^configurations/explorer/columnConfigs/(\d+)$', column_configurations_explorer)
   , url(r'^configurations/explorer/filterCombos$',        filter_combinations_explorer)
   , url(r'^configurations/explorer/filterCombos/(\d+)$',  filter_combinations_explorer)
   , url(r'^elective/([^/]+)/copy$',                       elective_copy)   
   , url(r'^projects/email$',                              projects_email)
   , url(r'^projects/time_accounting/([^/]+)$',            time_accounting)
   , url(r'^sessions/options$',                            get_options)
   , url(r'^sessions/time_accounting/([^/]+)$',            session_time_accounting)
   , url(r'^schedule/change_schedule$',                    change_schedule)
   , url(r'^schedule/shift_period_boundaries$',            shift_period_boundaries)
   , url(r'^schedule/email$',                              scheduling_email)
   , url(r'^receivers/schedule$',                          receivers_schedule)
   , url(r'^receivers/shift_date$',                        rcvr_schedule_shift_date)
   , url(r'^receivers/add_date$',                          rcvr_schedule_add_date)
   , url(r'^receivers/toggle_rcvr$',                       rcvr_schedule_toggle_rcvr)
   , url(r'^receivers/toggle_available$',                  rcvr_available_toggle)
   , url(r'^receivers/delete_date$',                       rcvr_schedule_delete_date)
   , url(r'^reservations$',                                reservations)
   , url(r'^period/([^/]+)/time_accounting$',              period_time_accounting)
   , url(r'^periods/publish$',                             publish_periods)
   , url(r'^periods/publish/(\d+)$',                       publish_periods)
   , url(r'^periods/restore_schedule',                     restore_schedule)
   , url(r'^window/([^/]+)/copy$',                         window_copy)
   , url(r'^projects$',               ProjectResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^projects/(\d+)$',         ProjectResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^sessions$',               SessionResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^sessions/(\d+)$',         SessionResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^periods/(UTC)$',          PeriodResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^periods/(ET)$',           PeriodResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^periods/(UTC)/(\d+)$',    PeriodResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^periods/(ET)/(\d+)$',     PeriodResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^windows$',                WindowResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^windows/(\d+)$',          WindowResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^windowRanges$',           WindowRangeResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^windowRanges/(\d+)$',     WindowRangeResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^users$',                  UserResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^users/(\d+)$',            UserResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^investigators$',          InvestigatorResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^investigators/([^/]+)$',  InvestigatorResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^friends$',                FriendResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^friends/([^/]+)$',        FriendResource(permitted_methods=('PUT', 'GET', 'POST')))
   , url(r'^electives$',              ElectiveResource(permitted_methods=('GET', 'PUT', 'POST')))
   , url(r'^electives/(\d+)$',        ElectiveResource(permitted_methods=('PUT', 'GET', 'POST')))
)
