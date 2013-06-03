from django.core.management import setup_environ
import settings
setup_environ(settings)

import psycopg2
import os
from datetime import datetime
from utilities.notifiers.Email import Email
from utilities.notifiers.emailNotifier import emailNotifier

def flaggedSessions(curr):
    q = """
    select s.name
    from pht_sessions as s
      join pht_session_flags as f on f.id = s.flags_id
    where f.thermal_night or
          f.rfi_night or
          f.optical_night or
          f.rfi_night or
          f.optical_night or
          f.transit_flat or
          f.guaranteed
    order by s.name
    """
    curr.execute(q)
    return [s for s, in curr.fetchall()]

def writeToFile(sessions):
    cmd = 'mv flaggedSessions_old.txt flaggedSessions_older.txt'
    os.system(cmd)
    cmd = 'mv flaggedSessions.txt flaggedSessions_old.txt'
    os.system(cmd)
    f = open('flaggedSessions.txt', 'w')
    f.write('%s\n%s' % (len(sessions), '\n'.join(sessions)))
    f.close()

def checkSessions(sessions):
    f = open('flaggedSessions_old.txt', 'r')
    contents = f.readlines()
    numSessions = int(contents[0].replace('\n', ''))
    if numSessions > len(sessions):
        soundTheAlarm(sessions, contents)
    f.close()

def soundTheAlarm(sessions, contents):
    body  = """
    The number of sessions with flags has gone down!

    from:
    %s

    to:
    %s
    """ % (''.join(contents), '%s\n%s' % (len(sessions), '\n'.join(sessions)))
    email = Email(sender = 'dss@gb.nrao.edu'
                , recipients = ['mmccarty@nrao.edu', 'pmargani@nrao.edu']
                , subject    = 'PHT Session Flags'
                , body       = body
                , date       = datetime.now()
                )
    emailN = emailNotifier(smtp = 'smtp.gb.nrao.edu')
    emailN.Send(email)
    
if __name__ == '__main__':
    conn = psycopg2.connect(host   = settings.DATABASES['default']['HOST']
                          , user   = settings.DATABASES['default']['USER']
                          , password = settings.DATABASES['default']['PASSWORD']
                          , database = settings.DATABASES['default']['NAME']
                          )
    curr     = conn.cursor()
    sessions = flaggedSessions(curr)
    writeToFile(sessions)
    checkSessions(sessions)
