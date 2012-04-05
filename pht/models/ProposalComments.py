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

class ProposalComments(models.Model):

    nrao_comment       = models.TextField(null = True)
    srp_to_pi          = models.TextField(null = True)
    srp_to_tac         = models.TextField(null = True)
    tech_review_to_pi  = models.TextField(null = True)
    tech_review_to_tac = models.TextField(null = True)
    tac_to_pi          = models.TextField(null = True)

    class Meta:
        db_table  = "pht_proposal_comments"
        app_label = "pht"

    @staticmethod
    def createFromSqlResult(result):
        """
        Creates a new ProposalComments instance initialized using the 
        result from an SQL query.
        """

        comments = ProposalComments(nrao_comment = result['comments'])
        comments.save()
        return comments
