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
    url = tinyurl.create_one('http://gbrescal.gb.nrao.edu/gbtobs/proposals.dbw?view=viewproposal&propcode=%s' % ps[0].session.project.pcode)
    update = 'Next observation: %s %s' % (title, url)
    twitter.Api(
        consumer_key        = settings.TWITTER['consumer_key']
      , consumer_secret     = settings.TWITTER['consumer_secret']
      , access_token_key    = settings.TWITTER['access_token_key']
      , access_token_secret = settings.TWITTER['access_token_secret']
    ).PostUpdate(update)
 
if __name__ == '__main__':
    TweetCurrentProject()
