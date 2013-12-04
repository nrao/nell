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

from lxml             import etree
from test_utils       import NellTestCase
from tools            import CurrentObsXML
from scheduler.models import Project

class TestCurrentObsXML(NellTestCase):

    def test_getCurrentObsInfo(self):

       co = CurrentObsXML.CurrentObsXML()

       p = Project.objects.all()[0]
       p.name = 'my title'
       p.abstract = 'my abstract'
       p.save()

       info = co.getCurrentObsInfo(project = p, useArchive = False)
       exp = {'source_name': 'unknown'
            , 'proposal_title': u'my title'
            , 'proposal_abstract': 'my abstract'
            , 'PI_institution': 'unknown'
            , 'source_dec': '0.0'
            , 'PI_name': 'unknown'
            , 'proposal_code': u'09A-001' # GBT09A-001
            , 'source_ra': '0.0'
             }
       self.assertEqual(exp, info)     

    def test_getXMLDoc(self):

       co = CurrentObsXML.CurrentObsXML()
       info = {'source_name': 'srcname'
            , 'proposal_title': u'my title'
            , 'proposal_abstract': 'my abstract'
            , 'PI_institution': 'unknown'
            , 'source_dec': '0.0'
            , 'PI_name': 'unknown'
            , 'proposal_code': u'09A-001'
            , 'source_ra': '0.0'
             }

       doc = co.getXMLDoc(info)
       docStr = etree.tostring(doc)
       exp = '<currently_observing telescope="GBT"><proposal_code>09A-001</proposal_code><proposal_title>my title</proposal_title><proposal_abstract>my abstract</proposal_abstract><PI_name>unknown</PI_name><PI_institution>unknown</PI_institution><source_name>srcname</source_name><source_ra>0.0</source_ra><source_dec>0.0</source_dec></currently_observing>'
       self.assertEqual(exp, docStr)

       self.assertTrue(co.validate(doc))

    def test_createProjectCode(self):

        co = CurrentObsXML.CurrentObsXML()

        p = "dog"
        self.assertEquals(p, co.createProjectCode(p))
 
        p = "GBTXXB-001"
        self.assertEquals(p, co.createProjectCode(p))
 
        p = "GBT13D-001"
        self.assertEquals(p, co.createProjectCode(p))
 
        p = "GBT13B-00X"
        self.assertEquals(p, co.createProjectCode(p))
 
        p = "GBT13B-001"
        self.assertEquals('13B-001', co.createProjectCode(p))
