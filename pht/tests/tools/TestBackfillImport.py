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

from django.test         import TestCase

from pht       import models as pht
from scheduler import models as scheduler
from pht.tools.database import BackfillImport
from scheduler.tests.utils    import create_sesshun

class TestBackfillImport(TestCase):

    fixtures = ['scheduler.json']

    def test_importProposals(self):
        session  = create_sesshun()

        # add some rcvrs
        rg = scheduler.Receiver_Group(session = session)
        rg.save()
        r = scheduler.Receiver.get_rcvr('L')
        rg.receivers.add(r)
        r = scheduler.Receiver.get_rcvr('X')
        rg.receivers.add(r)
        rg.save()

        backfill = BackfillImport(quiet = True)
        backfill.importProjects()
        for p in pht.Proposal.objects.all():
            p.delete()

