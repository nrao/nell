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

from django.db                 import models

from Proposal                  import Proposal
from SourceConvention          import SourceConvention
from SourceCoordinateEpoch     import SourceCoordinateEpoch
from SourceCoordinateSystem    import SourceCoordinateSystem
from SourceReferenceFrame      import SourceReferenceFrame
from SourceVelocityType        import SourceVelocityType
from pht.utilities             import *
from pht.utilities.Conversions import Conversions

class Source(models.Model):

    proposal          = models.ForeignKey(Proposal)
    pst_source_id     = models.IntegerField(null = True)
    target_name       = models.CharField(null = True, max_length = 2000)
    ra                = models.FloatField(null = True)
    dec               = models.FloatField(null = True)
    ra_range          = models.FloatField(null = True)
    dec_range         = models.FloatField(null = True)
    coordinate_epoch  = models.ForeignKey(SourceCoordinateEpoch, null = True)
    coordinate_system = models.ForeignKey(SourceCoordinateSystem, null = True)
    velocity_units    = models.ForeignKey(SourceVelocityType, null = True)
    velocity_redshift = models.FloatField(null = True)
    convention        = models.ForeignKey(SourceConvention, null = True)
    reference_frame   = models.ForeignKey(SourceReferenceFrame, null = True, max_length = 255)
    observed          = models.BooleanField(default = False)
    allowed           = models.NullBooleanField(null = True)
    # for storing raw string imported from PST
    pst_ra            = models.CharField(null = True, max_length = 255)
    pst_ra_range      = models.CharField(null = True, max_length = 255)
    pst_dec           = models.CharField(null = True, max_length = 255)
    pst_dec_range     = models.CharField(null = True, max_length = 255)

    class Meta:
        db_table  = "pht_sources"
        app_label = "pht"

    def __str__(self):
        return "%s at %5.2f : %5.2f" % (self.target_name
                                      , self.ra
                                      , self.dec)

    def allowedFromString(self, value):
        "Maps a string to our NullBooleanField"
        if value == 'allowed':
            self.allowed = True
        elif value == 'not allowed':
            self.allowed = False
        else:
            self.allowed = None

    def allowedToString(self):
        "Maps our NullBooleanField to a string"
        if self.allowed == True:
            return 'allowed'
        elif self.allowed == False:
            return 'not allowed'
        else:
            return 'unknown'

    @staticmethod
    def createFromSqlResult(proposal_id, result):
        """
        Creates a new Session instance initialized using the request from
        an SQL query.
        """

        c = Conversions()

        epoch = SourceCoordinateEpoch.objects.get(epoch = result['coordinate'])
        sys = SourceCoordinateSystem.objects.get(system = result['coordinate_system'])
        vType = SourceVelocityType.objects.get(type = result['velocity_type'])
        ref = SourceReferenceFrame.objects.get(frame = result['referenceFrame'])
        con = SourceConvention.objects.get(convention = result['convention'])
        
        # Occasionally this string can be something dumb like '?'
        try:
            vRedshift = float(result['velocity_redshift'])
        except:
            vRedshift = None

        source = Source(pst_source_id = result['source_id']
                          # Don't use result's because that's for the
                          # PST, not our GB PHT DB!
                        , proposal_id = proposal_id 
                        , target_name = result['target_name']
                        , ra = c.sexHrs2rad(result['right_ascension'])
                        , ra_range = c.sexHrs2rad(result['right_ascension_range'])
                        , dec = c.sexDeg2rad(result['declination'])
                        , dec_range = c.sexDeg2rad(result['declination_range'])
                        , coordinate_epoch = epoch 
                        , coordinate_system = sys 
                        , velocity_units = vType 
                        , velocity_redshift = vRedshift 
                        , convention = con 
                        , reference_frame = ref 
                        , pst_ra = result['right_ascension']
                        , pst_ra_range = result['right_ascension_range']
                        , pst_dec = result['declination']
                        , pst_dec_range = result['declination_range']
                        )

        source.save()
        return source
        
