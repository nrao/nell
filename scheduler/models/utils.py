from Receiver        import Receiver
from Period_Receiver import Period_Receiver

"""
    Why isn't this stuff in common.py?  Because the stuff in common.py is used by the models and
    the stuff in here is NOT used by the models at all.  These are utils which know about the models
    NOT the other way around.  Similar of the httpadapter, but has nothing to do with http-model
    data exchange.
"""

def init_rcvrs_from_session(session, period):
    "Use the session's rcvrs for the ones associated w/ this period."
    if session is None:
        return
    rcvrAbbrs = session.rcvrs_specified()
    for r in rcvrAbbrs:
        try:
            rcvr = Receiver.objects.get(abbreviation = r.strip())
        except Receiver.DoesNotExist:
            pass
        else:
            rp = Period_Receiver(receiver = rcvr, period = period)
            rp.save()
