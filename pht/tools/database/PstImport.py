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

from PstInterface     import PstInterface
from pht.models       import *
from scheduler.models import Observing_Type

class PstImport(PstInterface):

    def __init__(self, filename = "PstImport.txt", quiet = True, save = True):
        PstInterface.__init__(self)

        self.proposals = []

        # for reporting
        self.lines = []
        self.quiet = quiet
        self.save = save

    def initMap(self):
        

        # Need to map stuff from PST values to PHT values:
        # First, PST fronteds to PHT rcvr abbreviations
        self.frontendMap = {
            'L-Band (1.15-1.73 GHz)' : 'L'
          , 'PF1 340 MHz (0.290-0.395 GHz)' : '342' 
          , 'Q-Band (38.2-49.8 GHz)' : 'Q'
          , 'Ku-Band (12.0-15.4 GHz)' : 'Ku'
          , 'C-Band (3.95-5.85 GHz)' : 'C'
          , 'K-Band Lower (18.0-22.4 GHz)' : 'K'
          , 'Ka-Band MM-F1 (26.0-31.0 GHz)' : 'Ka'
          , 'PF2 (0.910-1.230 GHz)' : '1070'
          , 'S-Band (1.73-2.60 GHz)' : 'S' 
          , 'X-Band (8.0-10.0 GHz)' : 'X' 
          , 'Other' : 'None' 
          , 'Ka-Band MM-F2 (30.5-37.0 GHz)' : 'Ka' 
          , 'PF1 800 MHz (0.680-0.920 GHz)' : '800' 
          , 'PF1 600 MHz (0.510-0.690 GHz)' : '600' 
          , 'PF1 450 MHz (0.385-0.520 GHz)' : '450' 
          , 'K-Band Upper (22.0-26.5 GHz)' : 'K'
          , 'Ka-Band MM-F3 (36.0-40.0 GHz)' : 'Ka'
          , 'Ka-band - Zpectrometer' : 'Ka'
          , 'Ka-Band - Zpectrometer' : 'Ka'
          , 'Ka-Band - CCB' : 'Ka'
          , 'Mustang' : 'MBA'
          , 'KFPA' : 'KFPA' 
          , 'KFPA (shared risk)' : 'KFPA'
          , 'Mustang (90 GHz)' : 'MBA'
          , 'KFPA (18-26.5 GHz)' : 'KFPA'
          , 'W-band Shared Risk (68-92 GHz)' : 'W' 
          , 'Ka-Band - CCB (26.0-40.0 GHz)': 'Ka'
          , 'W-band MM4 (85-93.3 GHz)' : 'W'
          , 'W-band MM1 (67-74 GHz)' : 'W'
          , 'W-band MM2 (73-80 GHz)' : 'W'
       }

        # PST backends to PHT backend abbreviations
        self.backendMap = {
            'Berkeley-Caltech Pulsar Machine (BCPM)': 'None',
            'Caltech Continuum Backend (CCB)': 'CCB',
            'Caltech-Green Bank-Swinburne Recorder II (CGSR2)': 'CGSR2',
            'Digital Continuum Receiver (DCR)': 'DCR',
            'GBT Spectrometer - spectral line mode': 'gbtSpec',
            'GBT Spectrometer Spigot System': 'gbtSpec',
            'GUPPI': 'GUPPY',
            'Green Bank Astronomical Signal Processor (GASP)': 'GASP',
            'Mustang': 'Mustang',
            'Other': 'None',
            'Radar backend': 'Radar',
            'Spectral Processor - pulsar mode': 'gbtSpecP',
            'Spectral Processor - spectral line mode': 'gbtSpecP',
            'VEGAS': 'Vegas',
            'Zpectrometer': 'Zpect'}


    def importProposal(self, pcode, semester = None):
        """
        This method is responsible for querying the PST database to select
        all data associated with a given proposal.  The result are handed
        off to the Proposal model to create a new proposal in the GBPHT
        database initialized with the proposal data from the PST.
        """

        q = """
            select p.*, a.*, person.person_id
            from ((proposal as p 
              join author as a on p.principal_investigator_id = a.author_id)
              join userAuthentication as ua on ua.userAuthentication_id = a.user_id)
              join person on person.personAuthentication_id = ua.userAuthentication_id
            where PROP_ID = '%s'
            """ % pcode
        self.cursor.execute(q)
        row      = map(self.safeUnicode, self.cursor.fetchone())
        result   = dict(zip(self.getKeys(), row))
        pcode    = result['PROP_ID'].replace('/', '')

        try:
            proposal = Proposal.objects.get(pcode = pcode)
            proposal.delete()
        except Proposal.DoesNotExist:
            pass
        finally:
            proposal = Proposal.createFromSqlResult(result)
            if semester is None:
                # try to figure out what the semester is
                semester = self.semesterFromPcode(pcode)
            proposal.setSemester(semester)
            proposal.save()
            self.fetchAuthors(proposal)
            self.fetchScientificCategories(proposal)
            self.fetchObservingTypes(proposal)
            self.fetchSessions(proposal)
            self.fetchSources(proposal)
        
            self.proposals.append(proposal)
 
            self.report()

        return proposal

    def semesterFromPcode(self, pcode):
        """
        If the proposal code takes a form like GBT/12A-001, we should
        be able to figure out what the semester is.
        """
        try:
            semester = pcode.split("-")[0][-3:]
            assert semester[-1] in ['A','B','C']
        except:
            semester = None
        return semester    

    def importProposals(self, semester):
        """
        Imports all the GBT-related proposals in a given semester.
        """
        q = """
            select p.*,  a.*, person.person_id
            from ((proposal as p 
              join author as a on p.principal_investigator_id = a.author_id)
              join userAuthentication as ua on ua.userAuthentication_id = a.user_id)
              join person on person.personAuthentication_id = ua.userAuthentication_id
            where PROP_ID like '%%%s%%' and (p.TELESCOPE = 'GBT' or p.TELESCOPE = 'VLBA')
            order by PROP_ID
            """ % semester
        self.cursor.execute(q)
        keys = self.getKeys()
        for row in self.cursor.fetchall():
            results   = dict(zip(keys, map(self.safeUnicode, row)))
            pcode     = results['PROP_ID'].replace('/', '')
            try:
                prop = Proposal.objects.get(pcode = pcode)
            except Proposal.DoesNotExist:
                pid       = int(results['proposal_id'])
                telescope = results['TELESCOPE']
                if self.proposalUsesGBT(pid, telescope):            
                    proposal = Proposal.createFromSqlResult(results)
                    proposal.setSemester(semester)
                    self.fetchScientificCategories(proposal)
                    self.fetchObservingTypes(proposal)
                    self.fetchSessions(proposal)
                    self.fetchSources(proposal)
                    self.fetchAuthors(proposal)
                    self.proposals.append(proposal)

        self.report()

    def proposalUsesGBT(self, proposal_id, telescope):
        "Does at least one of the proposal's resources include the GBT?"
        # VLBA is a special case
        if telescope == "VLBA":
            return self.vlbaProposalUsesGBT(proposal_id)
        # This should work for GBT, VLA proposals (TBF: VLBI???)        
        q = """
            select r.TELESCOPE 
            from proposal as p, RESOURCES as r, sessionPair as sp, session as s 
            where sp.RESOURCE_GROUP = r.resource_group 
                AND s.session_id = sp.session_id 
                AND s.proposal_id = p.proposal_id 
                AND p.proposal_id = %d;
        """ % proposal_id
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for row in rows:
            if row[0].strip() == 'GBT':
                # all we need is one resource to be the GBT!
                return True
        # if we got here, no GBT resource!
        return False

    def getProposalId(self, pcode):
        "I need this all the time."
        q = "select proposal_id from proposal where PROP_ID = '%s'" % pcode
        self.cursor.execute(q)
        return self.cursor.fetchone()[0]

    def vlbaProposalUsesGBT(self, proposal_id):

        # VLBA doesn't use resource groups.  We can deal straight with 
        # the proposal
        q = """
        select v.GBT
        from (proposal as p join RESOURCES as r on r.PROPOSAL_ID = p.proposal_id) 
            join VLBA_RESOURCE as v on v.id = r.resource_id 
        where p.proposal_id = %d
        """ % proposal_id
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for row in rows:
            if row[0] == '\x01':
                # all we need is one to be the GBT!
                return True
        # if we got here, no GBT!
        return False

    def fetchAuthors(self, proposal):
        q = """
            select person.person_id, a.* 
            from (author as a 
              join userAuthentication as ua on ua.userAuthentication_id = a.user_id)
              join person on person.personAuthentication_id = ua.userAuthentication_id
            where proposal_id = %s
            """ % proposal.pst_proposal_id
        self.cursor.execute(q)
        keys = self.getKeys()
        for row in self.cursor.fetchall():
            author = Author.createFromSqlResult(dict(zip(keys, map(self.safeUnicode, row))), proposal)

    def fetchScientificCategories(self, proposal):
        q = """select scientificCategory 
               from scientificCategory
               where proposal_id = %s"""  % proposal.pst_proposal_id
        self.cursor.execute(q)
        for r in  self.cursor.fetchall():
            # commas are often used as deliminators, so replace them w/
            # something less problematic - but matches w/ our DB!
            category = r[0].replace(',', ';')
            cat, _ = ScientificCategory.objects.get_or_create(category = category)
            proposal.sci_categories.add(cat)
        proposal.save()

    def fetchObservingTypes(self, proposal):
        q = """select observingType 
               from observingType
               where proposal_id = %s"""  % proposal.pst_proposal_id
        self.cursor.execute(q)
        for r in  self.cursor.fetchall():
            try:
                proposal.observing_types.add(ObservingType.objects.get(type = r[0]))
            except ObservingType.DoesNotExist:
                ot = ObservingType(type = r[0])
                ot.save()
                proposal.observing_types.add(ot)
        proposal.save()

    def fetchSessions(self, proposal):
        "Attach associated sessions to this proposal"

        q = """select session_id 
               from session
               where MODIFIED_SESSION = false
               and proposal_id = %s""" % proposal.pst_proposal_id
        self.cursor.execute(q)
        # make sure session names are unique within the proposal
        names = {}
        for r in self.cursor.fetchall():
            sid = int(r[0])
            sess = self.importSession(proposal, sid)
            if sess.name in names.keys():
                current = names[sess.name]
                next = current + 1
                names[sess.name] = next  
                sess.name = "%s - %d" % (sess.name, next)
                sess.save()
            else:
                names[sess.name] = 1

    
    def importSession(self, proposal, sessId):
        """
        This method is responsible for querying the PST database to select
        all data associated with a given session.  The result are handed
        off to the Session model to create a new Session in the GBPHT
        database initialized with the session data from the PST.
        """

        q = """
            select s.*            
            from session as s
            where session_id = %d
            """ % sessId
        self.cursor.execute(q)
        row      = self.cursor.fetchone()
        rowDct = dict(zip(self.getKeys(), row))
        session = Session.createFromSqlResult(proposal.id, rowDct)
        # pass on other bits of info related to this query
        session.allotment = Allotment.createFromSqlResult(rowDct)
        session.target = Target.createFromSqlResult(rowDct)
        # other defaults
        session.semester     = proposal.semester
        flags = SessionFlags()
        flags.save()
        session.flags = flags
        day = SessionSeparation.objects.get(separation = 'day')
        m = Monitoring(outer_separation = day)
        m.save()
        session.monitoring = m
        n = SessionNextSemester()
        n.save()
        session.next_semester = n
        
        # other stuff
        self.importResources(session)
        session.save()

        # now we can determine it's types
        session.session_type = session.determineSessionType()
        session.weather_type = session.determineWeatherType()
        session.observing_type = session.determineObservingType()
        session.save()

        return session
    
    def importResources(self, session):
        "Get the front & back ends associated with this session."

        type = self.fetchTypeOfResource(session.pst_session_id)

        # if it ain't GBT, we don't bother
        if type is not None and type == 'GBT':
            self.importGBTResource(session)

    def fetchTypeOfResource(self, pst_sess_id):    
        "We need to know if this is for GBT or VLA, or what."

        q = """select r.TELESCOPE 
        from RESOURCES as r, sessionPair as sp, session as s 
        where sp.RESOURCE_GROUP = r.resource_group 
            AND s.session_id = sp.session_id 
            AND s.session_id = %d""" % pst_sess_id
        self.cursor.execute(q)
        rows = self.cursor.fetchone()
        if rows is None:
            return None
        return rows[0]

    def importGBTResource(self, session):
        "Turn PST resource info into our front & back end objects."

        # ignore resource groups, and just get the resources for 
        # this session
        q = """
        select gr.FRONT_END, gr.BACK_END 
        from GBT_RESOURCE as gr, sessionResource as sr 
        where gr.Id = sr.resource_id 
            AND sr.SESSION_ID = %d
        """ % session.pst_session_id

        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        self.initMap()
        for r in rows:
            # associate the front end w/ this session
            rcvr = self.frontendMap.get(r[0], None)
            if rcvr is not None and rcvr != 'None':
                rcvr = Receiver.get_rcvr(rcvr)
                session.receivers.add(rcvr)
                # default this receiver as granted
                session.receivers_granted.add(rcvr)
            # associate the front end w/ this session
            backend = self.backendMap.get(r[1], None)
            if backend is not None and backend != 'None':
                backend = Backend.objects.get(abbreviation = backend)
                session.backends.add(backend)
    
    def fetchSources(self, proposal):
        "Attach associated sources to this proposal."

        q = """select source_id 
               from source
               where proposal_id = %s""" % proposal.pst_proposal_id
        self.cursor.execute(q)
        for r in self.cursor.fetchall():
            sid = int(r[0])
            src = self.importSource(proposal, sid)
    
    def importSource(self, proposal, srcId):
        """/home/gbtlogs
        This method is responsible for querying the PST database to select
        all data associated with a given source.  T/home/gbtlogshe result are handed
        off to the Session model to create a new Session in the GBPHT
        database initialized with the session data /home/gbtlogsfrom the PST.
        """

        q = """
            select s.*            
            from source as s
            where source_id = %d
            """ % srcId
        self.cursor.execute(q)
        row      = self.cursor.fetchone()
        source   = Source.createFromSqlResult(proposal.id
                                            , dict(zip(self.getKeys()
                                                     , row)))
        # pass on the semester
        source.semester = proposal.semester

        source.save()

        return source

    def reimportAllSessionResources(self, semester):
        """
        This is a one-time needed function for fixing the fact that
        we had a bug in the original import, and now want to just
        reimport the session's resources.
        """
        ss = Session.objects.filter(proposal__semester__semester = semester).order_by('name')
        changes = {}
        for s in ss:
            # what are they now?
            rcvrs = s.get_receivers()
            backends = s.get_backends()
            changes[s.name] = {'old' : (rcvrs, backends)}
            # good, now get rid of them
            for r in s.receivers.all():
                s.receivers.remove(r)
            for b in s.backends.all():
                s.backends.remove(b)
            # now reimport them    
            self.importResources(s)            
            # what's it look like now?
            snew = Session.objects.get(id = s.id)
            rcvrs = snew.get_receivers()
            backends = snew.get_backends()
            changes[s.name]['new'] = (rcvrs, backends)

        # report
        filename = "reimportResources.txt"
        f = open(filename, 'w')
        changed = 0
        for k, v in changes.items():
            f.write("%s:\n" % k)
            if v['old'] != v['new']:
                changed += 1
                f.write("    Old: %s, %s\n" % (v['old'][0], v['old'][1]))
                f.write("    New: %s, %s\n" % (v['new'][0], v['new'][1]))
        f.write("Changed %d of %d sessions.\n" % (changed, len(ss)))    
        f.close()    

    def reportLine(self, line):
        "Add line to stuff to go into report file, and maybe to stdout too."
        if not self.quiet:
            print line
        self.lines.append(line)
            
    def report(self):
        "Write to a file, and/or stdout how the import went."

        now = datetime.utcnow()

        self.reportLine("*** PST IMPORT REPORT ***\n")
        self.reportLine("*** Summary ***\n")
        self.reportLine("Imported on %s\n" % now)
        self.reportLine("Imported %d Proposals\n" % len(self.proposals))
        numSessions = sum([len(p.session_set.all()) for p in self.proposals])
        self.reportLine("Imported %d Sessions\n" % numSessions)
        self.reportLine("\n");

        self.reportLine("*** Details ***\n")
        self.reportLine("Proposals Imported: \n")
        for p in self.proposals:
            self.reportLine("    %s\n" % p.pcode)
        self.reportLine("\n");

        # any problems converting?
        max_lst = [s.target.max_lst for p in self.proposals for s in p.session_set.all()]
        min_lst = [s.target.min_lst for p in self.proposals for s in p.session_set.all()]
        ra = [s.ra for p in self.proposals for s in p.source_set.all()]
        dec = [s.dec for p in self.proposals for s in p.source_set.all()]
        ra_range = [s.ra_range for p in self.proposals for s in p.source_set.all()]
        dec_range = [s.dec_range for p in self.proposals for s in p.source_set.all()]
        self.reportConversionStat('session.MAXIMUM_LST', max_lst)
        self.reportConversionStat('session.MINIMUM_LST', min_lst)
        self.reportConversionStat('source.right_ascension', ra)
        self.reportConversionStat('source.right_ascension_range', ra_range)
        self.reportConversionStat('source.declination', dec)
        self.reportConversionStat('source.declination_range', dec_range)

        # write it to the DB 
        if self.save:
            ir = ImportReport(create_date = now
                            , report = "".join(self.lines)
                             )
            ir.save()

    def reportConversionStat(self, field, values):    
        "How did converting a particular field go?"
        self.reportLine("Imported %d rows of field %s, failed: %d\n" % \
            (len(values), field, len([v for v in values if v is None])))
            
if __name__ == '__main__':
    import sys
    pst = PstImport()
    if sys.argv[1] == '1':
        p   = pst.importProposal(sys.argv[2], semester = '12A')
        print p
    elif sys.argv[1] == 'semester':
        pst.importProposals(sys.argv[2])
        print "%s proposals imported." % len(Proposal.objects.all())
