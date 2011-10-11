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

#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import Period
from datetime        import datetime, timedelta
import tinyurl
import twitter

def TweetCurrentProject():
    now   = datetime.utcnow()
    later = now + timedelta(hours = 1)

    ps = Period.objects.filter(state__abbreviation = 'S').filter(start__gte = now).filter(start__lt = later).filter(session__project__project_type__type = 'science').order_by('start')

    if len(ps) == 0: # Nothing sciency going on anytime soon.
        return

    title = ps[0].session.project.name[:100]
    pcode = ps[0].session.project.pcode
    update = 'Next observation: %s %s' % (pcode, title)
    twitter.Api(
        consumer_key        = settings.TWITTER['consumer_key']
      , consumer_secret     = settings.TWITTER['consumer_secret']
      , access_token_key    = settings.TWITTER['access_token_key']
      , access_token_secret = settings.TWITTER['access_token_secret']
    ).PostUpdate(update)
 
if __name__ == '__main__':
    TweetCurrentProject()
