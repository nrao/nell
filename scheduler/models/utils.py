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
