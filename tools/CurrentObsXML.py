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

from lxml                        import etree
from StringIO                    import StringIO
from datetime                    import datetime, timedelta
from utilities.database.external import GbtStatusDB
from scheduler.models            import *

class CurrentObsXML:

    """
    This class is responsible for gathering information on what is 
    currently observing on the GBT, and providing this information
    in a valid XML format, as specified by a schema.
    """

    def __init__(self, schema = None):

        self.schema = schema if schema is not None else self.getDefaultSchema()

        self.statusDB = GbtStatusDB()

    def getXMLString(self):
        "Returns (status, XMLString) of current observations"
        info = self.getCurrentObsInfo()
        xmlDoc = self.getXMLDoc(info)
        # validate
        print etree.tostring(xmlDoc)
        if not self.validate(xmlDoc):
           return (False, None)

        return (True, etree.tostring(xmlDoc))
           

    def getXMLDoc(self, info):
        "Returns xml tree based off dict of current obs. info"
        root = etree.Element("currently_observing", telescope="GBT")
        # shucks, order might matter
        keys = ["proposal_code", "proposal_title", "proposal_abstract", "PI_name", "PI_institution", "source_name", "source_ra", "source_dec"]
        #for key, value in info.items():
        for key in keys:
            subel = etree.Element(key)
            subel.text = info[key]
            root.append(subel)
        return root

    def validate(self, xmlDoc):
        "Is the given xml valid according to our schema?"

        # first, prepare the schema
        f = StringIO(self.schema)
        xmlschema_doc = etree.parse(f)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        # prepare the xmlDoc
        xmlStr = etree.tostring(xmlDoc)
        xmlStrIo = StringIO(xmlStr)
        doc = etree.parse(xmlStrIo)

        # and validate
        return xmlschema.validate(doc)

    def getCurrentObsInfo(self, project = None, now = None, useGbtStatus = True):
        "Returns the desired info in a dict."

        # get the current project observing
        if project is None:
            # get the project that's observing now
            if now is None:
                now = datetime.now()
            # first cast a wide net
            ps = Period.objects.filter(start__lt = now + timedelta(days=1), start__gt = now - timedelta(days=1), state__name = 'Scheduled').order_by('start')
            # now get the one you want
            ps = [p for p in ps if p.start < now and p.end() > now] 
            # TBF: check?
            p = ps[0]
            project = p.session.project

           
        # get all you can from DSS DB
        pcode = project.pcode
        title = project.name
        abstract = project.abstract
        pi = project.principal_investigator()
        piInst = "unknown"
        piName = "unknown"
        if pi is not None:
            piName = pi.display_name() 
            uInfo = pi.getStaticContactInfo()
            if len(uInfo['affiliations']) > 0:
                piInst = uInfo['affiliations'][0]


        # get the rest of other places (gbtstatus)
        if useGbtStatus:
            srcName, major, minor, epoch = self.statusDB.getSourceInfo()
        else:
            srcName, major, minor, epoch = ('unknown', '0.0 (RA)', '0.0 (DEC)', 'J2000')
        ra = dec = "unknown"
        if epoch == 'J2000':
            # get rid of the (Ra/Dec) part
            ra  = major.split(' ')[0]
            dec = minor.split(' ')[0]

        return dict(proposal_code=pcode
                  , proposal_title=title
                  , proposal_abstract=abstract
                  , PI_name=piName
                  , PI_institution=piInst
                  , source_name=srcName
                  , source_ra=ra
                  , source_dec=dec
                   )

    def getDefaultSchema(self):
        sch = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        
         <xs:element name="currently_observing">
          <xs:complexType>
           <xs:sequence>
           <xs:element name="proposal_code" type="xs:string"/>
           <xs:element name="proposal_title" type="xs:string" minOccurs="0"/>
           <xs:element name="proposal_abstract" type="xs:string" minOccurs="0"/>
           <xs:element name="PI_name" type="xs:string" minOccurs="0"/>
           <xs:element name="PI_institution" type="xs:string" minOccurs="0"/>
           <xs:element name="source_name" type="xs:string" minOccurs="0"/>
           <xs:element name="source_ra" type="xs:double"/>
           <xs:element name="source_dec" type="xs:double"/>
           </xs:sequence>
           <xs:attribute name="telescope" type="xs:string"/>
          </xs:complexType>
         </xs:element>
        
         <xs:simpleType name="telescopes">
          <xs:restriction base="xs:string">
           <xs:enumeration value="ALMA"/>
           <xs:enumeration value="VLA"/>
           <xs:enumeration value="VLBA"/>
           <xs:enumeration value="GBT"/>
           <xs:enumeration value="other"/>
          </xs:restriction>
         </xs:simpleType>
        
        </xs:schema>        
        """
        return sch

if __name__ == '__main__':

    co = CurrentObsXML()
    xmlStr = co.getXMLString()
    print xmlStr
