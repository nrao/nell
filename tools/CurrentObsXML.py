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
from utilities.TimeAgent         import *
from utilities.database.external import ArchiveDB
from utilities.database.external import AstridDB
from scheduler.models            import *

class CurrentObsXML:

    """
    This class is responsible for gathering information on what is 
    currently observing on the GBT, and providing this information
    in a valid XML format, as specified by a schema.
    """

    def __init__(self, schema = None):

        self.schema = schema if schema is not None else self.getDefaultSchema()

        self.archiveDB = ArchiveDB()
        self.astridDB  = AstridDB(dbname = "turtle")

        self.uri = "http://www.nrao.edu/namespaces/nrao"
        self.nsprefix = 'nrao'

    def getXMLString(self):
        "Returns (status, XMLString) of current observations"
        info = self.getCurrentObsInfo()
        xmlDoc = self.getXMLDoc(info)
        # validate
        #print etree.tostring(xmlDoc)
        if not self.validate(xmlDoc):
           return (False, None)

        return (True, self.xmlDoc2str(xmlDoc))
           

    def getXMLDoc(self, info):
        "Returns xml tree based off dict of current obs. info"
        # KLUGE: lxml doesn't put the namespace prefixes in, so we have to do 
        # this by hand; but 'nrao:' is invalid, so sticking in 'nrao-' now
        # then replacing '-' with ':'
        nsmap = {self.nsprefix : self.uri}
        root = etree.Element("%s-currently_observing" % self.nsprefix, nsmap=nsmap) #, telescope="GBT")
        # shucks, order might matter
        keys = ["telescope", "proposal_code", "proposal_title", "proposal_abstract", "PI_name", "PI_institution", "source_name", "source_ra", "source_dec"]
        for key in keys:
            subel = etree.Element("%s-%s" % (self.nsprefix, key))
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
        xmlStr = self.prepareXmlNamespace(xmlStr)
        xmlStrIo = StringIO(xmlStr)
        doc = etree.parse(xmlStrIo)

        # and validate
        return xmlschema.validate(doc)

    def xmlDoc2str(self, xmlDoc):
        return self.prepareXmlNamespace(etree.tostring(xmlDoc))

    def prepareXmlNamespace(self, xmlStr):
        "KLUGE: get the namepsace prefixes in there!"
        # by replacing the appropriate - with :
        xmlStr = xmlStr.replace("<nrao-", "<nrao:")
        xmlStr = xmlStr.replace("</nrao-", "</nrao:")
        return xmlStr

    def getMostRecentScienceProject(self, now = None):
        "We want the most recent science, not maintenance, testing, etc."

        if now is None:
            now = datetime.datetime.utcnow()

        # get all periods that have started in the past (the first of these is the current period)
        ps = Period.objects.filter(start__lt = now, state__abbreviation = 'S').order_by('-start')

        # go through these until you find a 'science' period
        sciencePeriod = None
        for p in ps:
            if self.isScienceObserving(p):
                sciencePeriod = p
                break

        return sciencePeriod.session.project if sciencePeriod is not None else None        

    def isScienceObserving(self, period):
        "Is this period for science and other factors?"
        p = period.session.project
        # make sure:
        #  * its science and not things like testing, maintenance, etc.
        #  * it has an entry in the PST: note that this works since all older projects
        #    that might not have an associated PHT proposal (that in turn gives the
        #    link to the PST) are completed, and shouldn't come up here.
        return p.is_science() and p.get_pst_proposal_id() is not None 
        
    def getCurrentObsInfo(self, project = None, start = None, useArchive = True):
        "Returns the desired info in a dict."

        # Init the info we need to get
        pcode = title = abstract = pi = piInst = piName = srcName = "unknown"
        ra = dec = '0.0'
        gbt = 'GBT'

        # get the current project observing
        if project is None:
            project = self.getMostRecentScienceProject(now = start)
            if project is None:
                # bail!
                return dict(proposal_code=pcode
                  , proposal_title=title
                  , proposal_abstract=abstract
                  , PI_name=piName
                  , PI_institution=piInst
                  , source_name=srcName
                  , source_ra=ra
                  , source_dec=dec
                  , telescope = gbt
                   )

        # get all you can from DSS DB
        pcode = self.createProjectCode(project.pcode)
        title = project.name
        abstract = project.abstract
        pi = project.principal_investigator()
        if pi is not None:
            piName = pi.display_name() 
            uInfo = pi.getStaticContactInfo()
            if len(uInfo['affiliations']) > 0:
                piInst = uInfo['affiliations'][0]


        # get the rest 
        if useArchive:
            # dont' try anything if you can't find the correct astrid code
            projectCode = self.astridDB.dssCode2astridCode(project.pcode)
            if self.astridDB.astridCodeExists(projectCode):
                srcName, ra, dec = self.archiveDB.getSourceInfo(projectCode
                                                              , start = start)
                ra = str(deg2rad(ra))
                dec = str(deg2rad(dec))

        return dict(proposal_code=pcode
                  , proposal_title=title
                  , proposal_abstract=abstract
                  , PI_name=piName
                  , PI_institution=piInst
                  , source_name=srcName
                  , source_ra=ra
                  , source_dec=dec
                  , telescope = gbt
                   )

    def createProjectCode(self, pcode):
        "Ex: GBT13B-001 -> 13B-001"

        # we need to convert project codes of the format:
        # <telescope><semester>-nnn
        #   where:
        #     <telescope> is something like GBT or VLBA
        #     <semester> is something like 12B, etc.
        #     nnn - is 001 through 999

        dash = pcode.find('-')
        if dash == -1:
            # this project code is not of the format '<tele><sem>-nnn'
            return pcode
        
        # check the semester
        sem = pcode[dash-3:dash]
        try:
            _ = int(sem[:2])
        except:
            return pcode
        if sem[2] not in ['A', 'B', 'C']:
            return pcode

        # check the number nnn
        try:
            _ = int(pcode[dash+1:])
        except:
            return pcode

        # okay, I think we can safely convert this project code now
        return pcode[dash-3:]

    def getDefaultSchema(self):
        sch = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema
  version         = "1.0"
  xmlns:xs        = "http://www.w3.org/2001/XMLSchema"
  targetNamespace = "http://www.nrao.edu/namespaces/nrao"
  xmlns:nrao      = "http://www.nrao.edu/namespaces/nrao"
  elementFormDefault = "qualified">

 <xs:simpleType name="telescopeType">
  <xs:restriction base="xs:string">
   <xs:enumeration value="ALMA"/>
   <xs:enumeration value="VLA"/>
   <xs:enumeration value="VLBA"/>
   <xs:enumeration value="GBT"/>
   <xs:enumeration value="other"/>
  </xs:restriction>
 </xs:simpleType>

 <xs:element name="currently_observing">
  <xs:complexType>
   <xs:sequence>
    <xs:element name="telescope" type="nrao:telescopeType"/>
    <xs:element name="proposal_code" type="xs:string"/>
    <xs:element name="proposal_title" type="xs:string" minOccurs="0"/>
    <xs:element name="proposal_abstract" type="xs:string" minOccurs="0"/>
    <xs:element name="PI_name" type="xs:string" minOccurs="0"/>
    <xs:element name="PI_institution" type="xs:string" minOccurs="0"/>
    <xs:element name="source_name" type="xs:string" minOccurs="0"/>
    <xs:element name="source_ra" type="xs:double"/>
    <xs:element name="source_dec" type="xs:double"/>
   </xs:sequence>
  </xs:complexType>
 </xs:element>
</xs:schema>"""
        return sch

if __name__ == '__main__':
    co = CurrentObsXML()
    xmlStr = co.getXMLString()
    print xmlStr
