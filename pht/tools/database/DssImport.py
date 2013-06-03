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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime         import datetime

from BackfillImport import BackfillImport
from PstInterface   import PstInterface
from pht.models       import *
from scheduler        import models as dss

class DssImport(object):

    def __init__(self, projects = [], quiet = True):
        self.quiet = quiet
        self.projects = projects
        self.backfill = BackfillImport()
        self.pst      = PstInterface()

    def importProjects(self):
        for p in self.projects:
            self.importProject(p)

    def importProject(self, project):
        proposal = Proposal.createFromDssProject(project, self.pst)
        self.backfill.importDssSessions(project, proposal)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tool for importing a DSS project into the GBPHT by pcode.')
    parser.add_argument('-p','--pcode', dest="pcode", help='Pcode of the project to import. (Ex. GBT12B-100)')

    args = parser.parse_args()

    if args.pcode is not None:
        project = dss.Project.objects.get(pcode = args.pcode)
        dss = DssImport(quiet = False)
        dss.importProject(project)
