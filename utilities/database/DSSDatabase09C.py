from utilities.database.DSSDatabase import DSSDatabase
from datetime                       import datetime
from sesshuns.models                import *

class DSSDatabase09C(DSSDatabase):

    """
    This class is responsible for adding any additional items to the database
    that is needed to run the DSS for this trimester.
    """

    def create(self):
        # do what always needs to get done
        DSSDatabase.create(self, "09C")
        # now the 09C specific stuff
        self.create_09C_rcvr_schedule()
        print "09C DB created."
    
    def create_09C_rcvr_schedule(self):
        "For each given date, what rcvrs are up?"

        rcvrChanges = []

        # First week - start a little early.
        #dt = datetime(2009, 10, 1, 16)
        dt = datetime(2009, 10, 1, 0)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        # "prelimonary[sic] receiver schedule for Oct - Jan"

        # Oct 7: C -> K
        dt = datetime(2009, 10, 7, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        # Oct 14: 1070 -> 800
        dt = datetime(2009, 10, 14, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Oct 26: 800 -> 450
        dt = datetime(2009, 10, 26, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '450'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 2: 450 -> 600
        dt = datetime(2009, 11, 2, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '600'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 4: Ku -> MBA? (Mustang)
        dt = datetime(2009, 11, 4, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '600'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 11: 600 -> 800
        dt = datetime(2009, 11, 11, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 24: 800 -> 342
        dt = datetime(2009, 11, 24, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Dec 13: 342 -> 800
        dt = datetime(2009, 12, 13, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Dec 27: 800 -> 342
        dt = datetime(2009, 12, 27, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 5: 342 -> 800
        dt = datetime(2010, 1, 5, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 6 (or Jan 21) Q-band    down, KFPA      up
        dt = datetime(2010, 1, 6, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 21 (or Feb 1) KFPA      down, Q-band    up
        dt = datetime(2010, 1, 21, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 24: 800 -> 342
        dt = datetime(2010, 1, 24, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Feb 1: 342 -> 1070
        dt = datetime(2010, 2, 1, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        for dt, rcvrs in rcvrChanges:
            for rcvr in rcvrs:
                r = first(Receiver.objects.filter(abbreviation = rcvr))
                rs = Receiver_Schedule(receiver = r, start_date = dt)
                rs.save()
                #print rs

