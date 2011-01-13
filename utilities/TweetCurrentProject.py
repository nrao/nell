#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *
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
        consumer_key = 'WQyTgOFR6k4ieBdvbELQ'
      , consumer_secret = 'roxz1TFCSQ9yOTpnwa67EbF3c1S5x8VGpVcjts'
      , access_token_key = '113465249-yfvjRkQAl2MYyJ5hEjGlEKyr0NNbKfyUehErM7oL'
      , access_token_secret = '2s9M5vPicohng2zOPICI5cvvgLp2NeMNRgd5bgnEq4'
    ).PostUpdate(update)
 
if __name__ == '__main__':
    TweetCurrentProject()
