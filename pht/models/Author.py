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
from pht.tools.database import PstInterface

class Author(models.Model):

    pst_person_id       = models.IntegerField()
    pst_author_id       = models.IntegerField(null = True)
    proposal            = models.ForeignKey('Proposal')
    affiliation         = models.CharField(max_length = 255, null = True)
    domestic            = models.BooleanField()
    new_user            = models.BooleanField()
    email               = models.CharField(max_length = 255)
    address             = models.CharField(max_length = 255, null = True)
    telephone           = models.CharField(max_length = 255)
    last_name           = models.CharField(max_length = 255, null = True)
    first_name          = models.CharField(max_length = 255, null = True)
    professional_status = models.CharField(max_length = 255, null = True)
    thesis_observing    = models.BooleanField()
    graduation_year     = models.CharField(max_length = 255, null = True)
    oldauthor_id        = models.CharField(max_length = 255)
    storage_order       = models.IntegerField()
    other_awards        = models.TextField(null = True)
    support_requester   = models.BooleanField()
    supported           = models.BooleanField()
    budget              = models.FloatField()
    assignment          = models.TextField(null = True)

    class Meta:
        db_table  = "pht_authors"
        app_label = "pht"

    def __str__(self):
        return "%s (%s)" % (self.getLastFirstName(), self.id)

    def getLastFirstName(self):
        return '%s, %s' % (self.last_name, self.first_name)

    @staticmethod
    def createFromSqlResult(result, proposal):
        """
        Creates a new Author instance initialized using the result from
        an SQL query.
        """
        author, _ = Author.objects.get_or_create(pst_person_id       = result['person_id']
                                               , pst_author_id       = result['author_id']
                                               , proposal            = proposal
                                               , affiliation         = result['AFFILIATION']
                                               , domestic            = result['DOMESTIC']
                                               , new_user            = result['NEW_USER']
                                               , email               = result['EMAIL']
                                               , address             = result['ADDRESS']
                                               , telephone           = result['TELEPHONE']
                                               , last_name           = result['LAST_NAME']
                                               , first_name          = result['FIRST_NAME']
                                               , professional_status = result['PROFESSIONAL_STATUS']
                                               , thesis_observing    = result['THESIS_OBSERVING']
                                               , graduation_year     = result['GRADUATION_YEAR']
                                               , oldauthor_id        = result['OLDAUTHOR_ID']
                                               , storage_order       = result['STORAGE_ORDER']
                                               , other_awards        = result['OTHER_AWARDS']
                                               , support_requester   = result['SUPPORT_REQUESTER']
                                               , supported           = result['SUPPORTED']
                                               , budget              = result['BUDGET']
                                               , assignment          = result['ASSIGNMENT']
                                               )
        return author

