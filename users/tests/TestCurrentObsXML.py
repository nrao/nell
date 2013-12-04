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
from StringIO         import StringIO
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
            , 'telescope': 'GBT'
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
            , 'telescope': 'GBT'
             }

       doc = co.getXMLDoc(info)
       docStr = co.xmlDoc2str(doc) #co.prepareXmlNamespace(etree.tostring(doc))
       exp = '<nrao:currently_observing xmlns:nrao="http://www.nrao.edu/namespaces/nrao"><nrao:telescope>GBT</nrao:telescope><nrao:proposal_code>09A-001</nrao:proposal_code><nrao:proposal_title>my title</nrao:proposal_title><nrao:proposal_abstract>my abstract</nrao:proposal_abstract><nrao:PI_name>unknown</nrao:PI_name><nrao:PI_institution>unknown</nrao:PI_institution><nrao:source_name>srcname</nrao:source_name><nrao:source_ra>0.0</nrao:source_ra><nrao:source_dec>0.0</nrao:source_dec></nrao:currently_observing>'
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

    def test_validate(self):

        # make sure that our class can validate example XML given by 
        # Stephan with schema given by Stephan
        xmlStr = """<?xml version="1.0" encoding="UTF-8"?>
<nrao:currently_observing xmlns:nrao="http://www.nrao.edu/namespaces/nrao">
 <nrao:telescope>VLA</nrao:telescope>
 <nrao:proposal_code>13B-001</nrao:proposal_code> 
 <nrao:proposal_title>This is my fancy title.</nrao:proposal_title>
 <nrao:proposal_abstract>This is my fancy abstract.</nrao:proposal_abstract>
 <nrao:PI_name>Stephan Witz</nrao:PI_name>
 <nrao:PI_institution>NRAO</nrao:PI_institution>
 <nrao:source_name>TEST</nrao:source_name>
 <nrao:source_ra>0.0000</nrao:source_ra>
 <nrao:source_dec>0.0000</nrao:source_dec>
</nrao:currently_observing>"""

        xmlStrIo = StringIO(xmlStr)
        doc = etree.parse(xmlStrIo)

        co = CurrentObsXML.CurrentObsXML()
        
        self.assertTrue(co.validate(doc))
