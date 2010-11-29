from sesshuns.models         import *

class WindowAlerts():

    """
    This class is responsible for both finding issues with windows and
    constraints (enable flag, blackouts, etc.), and sending notifications
    concerning these issues.
    """
   
    def __init__(self):

        # two stages for alerts; how many days before start of window 
        # to go from stage I to stage II?
        self.stageBoundary = 15
 
        self.now = datetime.utcnow()
        
        self.wins = Window.objects.all()

    def getWindowTimes(self):
        """
        Returns the stats on windows.
        For use in determining if alerts are raised.
        """
       
        # we really only care about windows that are not complete
        wins = Window.objects.filter(complete = False)
        return zip(wins
                , [w.getBlackedOutSchedulableTime() for w in wins])

    def findAlerts(self):
        """
        Gets the stats on windows, and examines them to see if
        an alarm needs to be raised.
        """

        stats = self.getWindowTimes()
        alerts = []
        for w, stat in stats:
            hrsSchedulable = stat[0]
            hrsBlacked = stat[1]
            ratio = hrsBlacked/hrsSchedulable

            if ratio > .10 and ratio < .50:
                alerts.append((w, stat, 1))
            elif ratio > .50:
                alerts.append((w, stat, 2))
            else:
                pass
        return alerts 

    def raiseAlerts(self, stage = 1, now = None, notify = True):
        """
        Finds problems with windows, and sends out emails.
        Emails will be sent to observers once per week (Monday morning)
        until 15 days before the window start date. (Stage I)
        Emails will be sent daily to all project investigators =< 15 
        days before the window end date. (Stage II)
        """

        # Just two stages (see comment above)
        assert stage in (1, 2)

        alerts = self.findAlerts()

        now = now if now is not None else datetime.utcnow()
        today = datetime(now.year, now.month, now.day)

        notifications = []
        if stage == 1:
            for w, stat, level in alerts:
                daysTillStart = (w.start_datetime() - today).days
                if daysTillStart > self.stageBoundary:
                    notifications.append((w, stat, level, 1))
                    # send email
                    if notify:
                        pass
        elif stage == 2:
            for w, stat, level in alerts:
                daysTillStart = (w.start_datetime() - today).days
                if daysTillStart <= self.stageBoundary:
                    notifications.append((w, stat, level, 2))
                    # send email
                    if notify:
                        pass
                    
        return notifications                    


                



       
