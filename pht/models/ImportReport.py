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

from pht.utilities import *

class ImportReport(models.Model):

    create_date = models.DateTimeField(null = True)
    report      = models.TextField(null = True)

    class Meta:
        db_table  = "pht_import_reports"
        app_label = "pht"

    def __str__(self):
        return "Report from %s" % self.create_date

    def jsonDict(self):
        return {'id'          : self.id
              , 'create_date' : datetime2ExtDatetime(self.create_date)
              , 'report'      : self.report
               }

    @staticmethod
    def jsonDictOptions():
        return [s.jsonDict() for s in ImportReport.objects.all().order_by('-create_date')]
            