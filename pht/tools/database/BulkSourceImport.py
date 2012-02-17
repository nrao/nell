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

from pht.models   import *

class BulkSourceImport:

    """
    Responsible for loading Source objects into the PHT via a text file.
    Uses the same format as the PST.  From that tool's docs:

    Each line of the file should follow the format:
    SourceName; Group Names; Coordinate System; Equinox; Longitude; Latitude; Ref Frame; Convention; Velocity;

    For example:
    NGC3242; PNe; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;
    NGC3242 ; PNe ; Equatorial ; J2000 ; 10:24:46.1 ; -18:38:32 ; Barycentric ; Optical ; 4.70;
    NGC3242 Pos1; G1, G2, G3; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;
    """

    def __init__(self, filename = None, pcode = None):

        self.filename = filename
        self.pcode = pcode

        self.sources = []

    def importSources(self, pcode = None, filename = None): 
        "Import sources from the given file"

        if filename is not None:
            self.filename = filename
        if pcode is not None:
            self.pcode = pcode

        # TBF: when we deploy, any special file management needed?
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()
        
        self.importSourcesFromLines(line)
            
    def importSourcesFromLines(self, lines):
        "Each of the given lines could be imported as a new source."

        # which proposal are these sources for?
        proj = Proposal.objects.get(pcode = self.pcode)

        for i, l in enumerate(lines):
            src, error = self.tryImportFromLine(l, i, proj.id)
            # if there are any signs of trouble, clean up and leave
            if src is None or error is not None:
                self.cleanUp()
                return (False, error)
            else:
                self.sources.append(src)
 
        # success
        return (True, None)

    def cleanUp(self):
        "Make sure you leave things the way you found them."
        for s in self.sources:
            s.delete()
        self.sources = []    

    def tryImportFromLine(self, line, lineNum, proposalId):

        # make sure you can recover from *any* error so that you 
        # can clean up properly
        try:
            src = self.importFromLine(line, proposalId)
            error = None
        except Exception, e:
            src = None
            error = "Error on line %d: %s" % (lineNum, str(e))
        return (src, error)

    def importFromLine(self, line, proposalId):    

        parts = line.split(';')

        # Each line of the file should follow the format:
        # SourceName; Group Names; Coordinate System; Equinox; Longitude; Latitude; Ref Frame; Convention; Velocity;
        # let the last ';' be optional
        assert len(parts) in [9, 10], "Missing values; should be 9 per line"

        # here's the trick we'll use: we'll recreate the dictionary
        # that results from our SQL query when importing from 
        # the PST DB, then reuse our static create method.
        # First, the fields we just parsed:
        dct = dict(
            target_name = parts[0].strip()
            # skipping group
          , coordinate_system = parts[2].strip()
          , coordinate = parts[3].strip()
          , right_ascension = parts[4].strip()
          , declination = parts[5].strip()
          , referenceFrame = parts[6].strip()
          , convention = parts[7].strip()
          , velocity_redshift = parts[8].strip()
          # then the stuff we'll have to default
          , source_id = None
          , right_ascension_range = ''
          , declination_range = ''
          , velocity_type = 'Velocity' 
        )

        src = Source.createFromSqlResult(proposalId, dct)

        return src


        
