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
        self.badFrontends = []
        self.badBackends = []

        self.thermalNightRcvrs = ['W', 'MBA', 'MBA1.5']

        # for reporting
        self.lines = []
        self.quiet = quiet
        self.save = save

    def initMap(self):
        

        # Need to map stuff from PST values to PHT values:
        # First, PST fronteds to PHT rcvr abbreviations
        self.frontendMap = {
              'C-Band (3.95-5.85 GHz)'          : 'C'
            , 'C-band (3.95-5.85 GHz)'          : 'C'
            , 'C-band Shared Risk (5.85-8 GHz)' : 'C'
            , 'K-Band Lower (18.0-22.4 GHz)'    : 'K'
            , 'K-Band Upper (22.0-26.5 GHz)'    : 'K'
            , 'Ka-Band - CCB'                   : 'Ka'
            , 'Ka-Band - CCB (26.0-40.0 GHz)'   : 'Ka'
            , 'Ka-band - Zpectrometer '         : 'Ka'
            , 'Ka-Band MM-F1 (26.0-31.0 GHz)'   : 'Ka'
            , 'Ka-Band MM-F2 (30.5-37.0 GHz)'   : 'Ka'
            , 'Ka-Band MM-F3 (36.0-40.0 GHz)'   : 'Ka'
            , 'Ka-Band - Zpectrometer'          : 'Ka'
            , 'KFPA'                            : 'KFPA'
            , 'KFPA (18-26.5 GHz)'              : 'KFPA'
            , 'KFPA (shared risk)'              : 'KFPA'
            , 'Ku-Band (12.0-15.4 GHz)'         : 'Ku'
            , 'Ku-band Shared Risk (12-18 GHz)' : 'Ku'
            , 'Ku-wideband Shared Risk (11-18 GHz)' : 'KuWide'
            , 'L-Band (1.15-1.73 GHz)'          : 'L'
            , 'Mustang'                         : 'MBA'
            , 'Mustang (90 GHz)'                : 'MBA'
            , 'Mustang 1.5'                     : 'MBA1.5'
            , 'Other'                           : 'None'
            , 'PF1 340 MHz (0.290-0.395 GHz)'   : '342'
            , 'PF1 450 MHz (0.385-0.520 GHz)'   : '450'
            , 'PF1 600 MHz (0.510-0.690 GHz)'   : '600'
            , 'PF1 800 MHz (0.680-0.920 GHz)'   : '800'
            , 'PF2 (0.910-1.230 GHz)'           : '1070'
            , 'Q-Band (38.2-49.8 GHz)'          : 'Q'
            , 'S-Band (1.73-2.60 GHz)'          : 'S'
            , 'W-band MM1 (67-74 GHz)'          : 'W'
            , 'W-band MM2 (73-80 GHz)'          : 'W'
            , 'W-band MM3 (79-86 GHz)'          : 'W'
            , 'W-band MM4 (85-93.3 GHz)'        : 'W'
            , 'W-band Shared Risk (68-92 GHz)'  : 'W'
            , 'X-Band (8.0-10.0 GHz)'           : 'X'
        }
        self.frontendMapLower = dict([(k.lower(), v) for k, v in self.frontendMap.iteritems()])


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
            'VEGAS Shared Risk': 'Vegas',
            'GBT VEGAS Shared Risk': 'Vegas',
            'Zpectrometer': 'Zpect'}
        self.backendMapLower = dict([(k.lower(), v) for k, v in self.backendMap.iteritems()])

    def importProposalsByPhtPcode(self, pcodes):
        "Handles differences in PST/PHT pcodes"
        # add / where needed
        pcodes = [pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/') for pcode in pcodes]
        self.importProposalsByPcode(pcodes)
            
    def importProposalsByPcode(self, pcodes):
        "Imports using a list of project codes"
        for pcode in pcodes:
            self.importProposal(pcode)
        self.report()

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
            where PROP_ID = '%s' or LEGACY_ID = '%s'
            """ % (pcode, pcode)
        self.cursor.execute(q)
        row      = map(self.safeUnicode, self.cursor.fetchone())
        result   = dict(zip(self.getKeys(), row))
        result['PROP_ID'] = pcode # Always use the given pcode

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
            self.fetchComments(proposal, propQueryResults = result)
            self.fetchAuthors(proposal)
            self.fetchScientificCategories(proposal)
            self.fetchObservingTypes(proposal)
            self.fetchSources(proposal)
            self.fetchSessions(proposal)
            self.fetchSRPScore(proposal)
        
            self.proposals.append(proposal)
 
            # We no longer create a report from this lower-level func.
            #self.report()

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
        # init reporting
        self.lines = []
        q = """
            select p.*,  a.*, person.person_id
            from ((proposal as p 
              join author as a on p.principal_investigator_id = a.author_id)
              join userAuthentication as ua on ua.userAuthentication_id = a.user_id)
              join person on person.personAuthentication_id = ua.userAuthentication_id
            where PROP_ID like '%%%s%%' and 
              (p.TELESCOPE = 'GBT' or p.TELESCOPE = 'VLBA' or p.TELESCOPE = 'GMVA')
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
                    self.fetchComments(proposal, propQueryResults = results)
                    self.fetchScientificCategories(proposal)
                    self.fetchObservingTypes(proposal)
                    self.fetchSources(proposal)
                    self.fetchSessions(proposal)
                    self.fetchAuthors(proposal)
                    self.fetchSRPScore(proposal)
                    self.proposals.append(proposal)

        self.report()

    def proposalUsesGBT(self, proposal_id, telescope):
        "Does at least one of the proposal's resources include the GBT?"
        if telescope == "VLBA":
            return self.vlbaProposalUsesGBT(proposal_id)
        elif telescope == "GMVA":
            return self.gmvaProposalUsesGBT(proposal_id)
        else: # GBT
            return self.gbtProposalUsesGBT(proposal_id)

    def gbtProposalUsesGBT(self, proposal_id):
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

    def gmvaProposalUsesGBT(self, proposal_id):
        q = """
        SELECT prop_id 
        FROM proposal, RESOURCES, GMVA_RESOURCE 
        WHERE proposal.proposal_id = RESOURCES.proposal_id 
          AND GMVA_RESOURCE.Id = RESOURCES.resource_id 
          AND GMVA_RESOURCE.GREEN_BANK = b'1'
          AND proposal.proposal_id = %d
        """ % proposal_id
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        return len(rows) > 0

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

    def importDispositions(self, semester):
        "Import Dispositions fro already imported proposals"

        # we only get dispostions for those proposals that:
        #   * came out of the PST
        #   * have been transferred to the DSS
        proposals = Proposal.objects.filter(semester__semester = semester).exclude(pst_proposal_id = 0).exclude(pst_proposal_id = None).exclude(dss_project = None).order_by('pcode')
        map(self.fetchDisposition, proposals)

    def fetchDisposition(self, proposal):
        "Grab the dispostion letter and associate it to the DSS Project"

        # nothing to get? or nowhere to put it?
        if proposal.pst_proposal_id is None \
            or proposal.dss_project is None:
            return 

        query = "select disposition_letter from proposal where proposal_id = %s" \
            % proposal.pst_proposal_id

        self.cursor.execute(query)
        row    = self.cursor.fetchone()
        disposition = self.safeUnicode(row[0])
        proposal.dss_project.disposition = disposition 
        proposal.dss_project.save()

    def importSRPRelatedInfo(self, semester):
        "Import SRP related info for already imported proposals"
        proposals = Proposal.objects.filter(semester__semester = semester).exclude(pst_proposal_id = 0).exclude(pst_proposal_id = None)
        map(self.fetchSRPScore, proposals)
        map(self.fetchSRPRelatedCommentsForProposal, proposals)

    def fetchSRPRelatedCommentsForProposal(self, proposal):
        """
        Used for getting SRP comments from PST for a proposal
        already in the GB PHT.
        """

        # nothing to get?
        if proposal.pst_proposal_id is None:
            return 

        if proposal.comments is None:
            comments = ProposalComments()
            proposal.comments = comments
            proposal.save()

        srps = self.fetchSRPComments(proposal.pst_proposal_id)
        if srps is not None:
            proposal.comments.srp_to_pi  = srps[0]
            proposal.comments.srp_to_tac = srps[1]
            proposal.comments.save()
        tech = self.fetchTechnicalReviews(proposal.pst_proposal_id)
        if tech is not None:
            proposal.comments.tech_review_to_pi  = tech[0]
            proposal.comments.tech_review_to_tac = tech[1]
            proposal.comments.save()

    def fetchComments(self, proposal, propQueryResults = None):

        pid = int(proposal.pst_proposal_id)
        
        if propQueryResults is None:
            row = self.fetchNRAOComments(proposal)
            keys = self.getKeys()
            propQueryResults   = dict(zip(keys, map(self.safeUnicode, row)))

        # initialize the object for all comments
        comments = ProposalComments.createFromSqlResult(propQueryResults)
        comments.save()

        # fill it up with the rest of the comments
        srps = self.fetchSRPComments(pid)
        if srps is not None:
            comments.srp_to_pi  = srps[0]
            comments.srp_to_tac = srps[1]
        tech = self.fetchTechnicalReviews(pid)
        if tech is not None:
            comments.tech_review_to_pi  = tech[0]
            comments.tech_review_to_tac = tech[1]

        # save it off
        comments.save()
        proposal.comments = comments
        proposal.save()

    def fetchNRAOComments(self, proposal):
        q = "SELECT comments FROM proposal WHERE proposal_id = %d" \
            % proposal.pst_proposal_id
        self.cursor.execute(q)
        return self.cursor.fetchone()

    def fetchSRPScore(self, proposal):
        q = """
            SELECT
              tr.normalizedSRPScore as score,
              pns.srpScores as srpScores
            FROM (proposal AS p
            LEFT JOIN proposal_tac_reviews AS tr ON p.proposal_id = tr.proposal_id)
            LEFT JOIN proposal_normalized_scores AS pns ON p.proposal_id = pns.proposal_id
            WHERE p.proposal_id = '%s'
            """ % proposal.pst_proposal_id
        self.cursor.execute(q)
        row    = self.cursor.fetchone()
        rowDct = dict(zip(self.getKeys(), row))
        proposal.normalizedSRPScore       = rowDct['score']
        proposal.draft_normalizedSRPScore = rowDct['srpScores']

        q = """
            select count(*) as numrefs from proposal_reviews where proposal_id = %s
            """ % proposal.pst_proposal_id
        self.cursor.execute(q)
        row    = self.cursor.fetchone()
        rowDct = dict(zip(self.getKeys(), row))
        proposal.num_refs = rowDct['numrefs']
        proposal.save()

    def fetchAuthors(self, proposal):
        "While creating PHT authors for this proposal, also mark who is the contact"
        # what id are we watching out for, so we can assign contact?
        contactId = self.getPrincipalContactId(proposal)
        # now query for all the authors
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
            result = dict(zip(keys, map(self.safeUnicode, row)))
            author = Author.createFromSqlResult(result, proposal)
            # is this author actually the contact as well?
            if int(author.pst_author_id) == contactId:
                proposal.contact = author
                proposal.save()

    def getPrincipalContactId(self, proposal):
        q = """
            select contact_id 
            from proposal
            where proposal_id = '%s'
            """ % proposal.pst_proposal_id
        self.cursor.execute(q)
        r = self.cursor.fetchone()
        return int(r[0])

    def fixAuthorsBits(self):
        """
        The author booleans got messed up when we originally import authors.  
        This method fixes them.
        """
        for a in Author.objects.all():
            q   = "select * from author where author_id = %s" % a.pst_author_id
            self.cursor.execute(q)
            keys = self.getKeys()
            row = self.cursor.fetchone()
            result = dict(zip(keys, map(self.safeUnicode, row)))
            a.domestic = result['DOMESTIC'] == '\x01'
            a.new_user = result['NEW_USER'] == '\x01'
            a.thesis_observing = result['THESIS_OBSERVING'] == '\x01'
            a.support_requester = result['SUPPORT_REQUESTER'] == '\x01'
            a.supported = result['SUPPORTED'] == '\x01'
            a.save()

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
        self.importSessionSources(session)
        session.save()

        # now we can determine it's types
        session.session_type = session.determineSessionType()
        session.weather_type = session.determineWeatherType()
        session.observing_type = session.determineObservingType()
        session.save()

        return session
    

    def importSessionSources(self, session):
        "Get the sources associated with this session."
        q = "select source_id from sessionSource where SESSION_ID = %s" % session.pst_session_id
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for source_id, in rows:
            source = session.proposal.source_set.get(pst_source_id = source_id)
            session.sources.add(source)
            session.save()
        session.averageRaDec(session.sources.all())

    def importResources(self, session):
        "Get the front & back ends associated with this session."

        # Assume this is a GBT session and try to import its resources
        success = self.importGBTResource(session)

        # If we failed to import the GBT resources assume its VLBA
        if not success:
            b = Backend.objects.get(abbreviation = 'gbtVLBA')
            session.backends.add(b)
            session.save()

    def fetchTypeOfResource(self, pst_sess_id):    
        "We need to know if this is for GBT or VLA, or what."
        # This relation is not always set in the PST.  Use at your own risk.

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

    def findReceiver(self, rx):
        rcvr = self.frontendMap.get(rx) or self.frontendMapLower.get(rx.lower())
        if rcvr is None:
            for k, v in self.frontendMap.iteritems():
                if v.lower() + '-band' in rx.lower():
                    rcvr = v
                    break
        return rcvr

    def findBackend(self, backend):
        backend = self.backendMap.get(backend) or self.backendMapLower.get(backend.lower())
        return backend

    def importGBTResource(self, session):
        "Turn PST resource info into our front & back end objects."

        # ignore resource groups, and just get the resources for 
        # this session
        q = """
        select gr.FRONT_END, gr.BACK_END, gr.RECEIVER_OTHER 
        from GBT_RESOURCE as gr, sessionResource as sr 
        where gr.Id = sr.resource_id 
            AND sr.SESSION_ID = %d
        """ % session.pst_session_id
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        self.initMap()
        for r in rows:
            # associate the front end w/ this session
            if str(r[0]).strip() == 'Other':
                # special case: use what they gave as the 'other'
                other = str(r[2]).strip()
                session.other_receiver = other
            else:    
                rcvr = self.findReceiver(r[0])
                if rcvr is not None and rcvr != 'None':
                    rcvr = Receiver.get_rcvr(rcvr)
                    session.receivers.add(rcvr)
                    # default this receiver as granted
                    session.receivers_granted.add(rcvr)
                    self.checkForNightTimeRx(session, rcvr)
                elif rcvr is None:
                    self.badFrontends.append((session, r[0]))
            # associate the back end w/ this session
            backend = self.findBackend(r[1])
            if backend is not None and backend != 'None':
                backend = Backend.objects.get(abbreviation = backend)
                session.backends.add(backend)
            elif backend is None:
                self.badBackends.append((session, r[1]))
        return True
    
    def checkForNightTimeRx(self, session, rcvr):
        if rcvr.abbreviation in self.thermalNightRcvrs:
            session.flags.thermal_night = True
            session.flags.save()

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

    def fetchTechnicalReviews(self, proposal_id):

        q = """
        SELECT tr.commentsForAuthors, tr.commentsForTAC
        FROM technical_reviews as tr, 
             proposal_reviews as pr, 
             proposal as p 
        WHERE pr.review_id = tr.review_id 
            AND pr.proposal_id = p.proposal_id 
            AND p.proposal_id = %d
        """ % proposal_id
        self.cursor.execute(q)
        # collect the possibly mutliple reviews
        result = None
        pi = ''
        tac = ''
        rows = self.cursor.fetchall()
        for row in rows:
            if row[0] is not None and row[1] is not None:
                pi  += ' \n' + row[0]
                tac += ' \n' + row[1]
            if pi != '' and tac != '':
                result = (pi, tac)
        return result    

    def fetchSRPComments(self, proposal_id):

        q = """
        SELECT sc.commentsForAuthors, sc.commentsForTac
        FROM srp_comments as sc,
             proposal as p,
             proposal_normalized_scores as pns,
             srp_comments_map as scm 
         WHERE scm.normalized_scores_id = pns.normalized_scores_id 
             AND  pns.proposal_id = p.proposal_id 
             AND sc.srp_comments_id = scm.srp_comments_id 
             AND p.proposal_id = %d
        """ % proposal_id
        self.cursor.execute(q)
        return self.cursor.fetchone()

    def checkPst(self, pcode):
        pcode = pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/')
        q = "select count(*) from proposal where PROP_ID = '%s' or LEGACY_ID = '%s'" % (pcode, pcode)
        self.cursor.execute(q)
        result = self.cursor.fetchone()
        return result[0] == 1

    def reimportAllSessionResources(self, semester, sessions = None):
        """
        This is a one-time needed function for fixing the fact that
        we had a bug in the original import, and now want to just
        reimport the session's resources.
        """

        if sessions is None:
            ss = Session.objects.filter(proposal__semester__semester = semester).order_by('name')
        else:
            ss = sessions

        reimported = []
        changes = {}
        for s in ss:
            reimported.append(s) 
            key = "%s (%s)" % (s.name, s.proposal.pcode)
            # what are they now?
            rcvrs = s.get_receivers()
            backends = s.get_backends()
            changes[key] = {'old' : (rcvrs, backends)}
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
            changes[key]['new'] = (rcvrs, backends)

        # report
        filename = "reimportResources.txt"
        f = open(filename, 'w')
        changed = 0
        f.write("Reimported sources for sessions:\n")
        for s in reimported:
            f.write(    "%s (%s)\n" % (s.name, s.proposal.pcode))
        f.write("Actual Changes:\n")
        for k, v in changes.items():
            if v['old'] != v['new']:
                f.write("%s:\n" % k)
                changed += 1
                f.write("    Old: %s, %s\n" % (v['old'][0], v['old'][1]))
                f.write("    New: %s, %s\n" % (v['new'][0], v['new'][1]))
        f.write("Changed %d of %d sessions.\n" % (changed, len(ss)))    
        f.close()    

    def importAllContacts(self):
        "For adding contacts to already imported proposals"
        ps = Proposal.objects.all().order_by('pcode')
        for p in ps:
            self.importContact(p)

    def importContact(self, proposal):
        "Import the contact for the given proposal"
        if proposal.pst_proposal_id is None:
            return

        q = """
            select p.contact_id 
            from proposal as p
            where p.proposal_id = %d
            order by p.PROP_ID
        """ % proposal.pst_proposal_id
        try:
            self.cursor.execute(q)
            r = self.cursor.fetchone()
            # contact for this proposal?
            if r is not None:
                # who IS the contact?
                authors = Author.objects.filter(pst_author_id = int(r[0]))
                if len(authors) == 1:
                    author = authors[0]
                elif len(authors) == 0:
                    author = None
                    print "No contact for ", proposal.pcode
                else:
                    author = authors[0]
                    print "Too many authors: ", proposal.pcode, authors
                # assign the contact    
                print proposal.pcode, r, author
                proposal.contact = author
                proposal.save()
                if proposal.contact != proposal.pi:
                    print "PI Different: ", proposal.pi
        except:
            print "Exception with proposal: ", proposal

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

        self.reportLine("\nNumber of unrecognized frontends: %d\n" % len(self.badFrontends))
        for s, b in self.badFrontends:
            self.reportLine("    %s : %s" % (s, b)) 
        self.reportLine("\nNumber of unrecognized backends: %d\n" % len(self.badBackends))
        for s, b in self.badBackends:
            self.reportLine("    %s : %s" % (s, b)) 

        # write it to the DB 
        if self.save:
            ir = ImportReport(create_date = now
                            , report = "".join(self.lines)
                             )
            ir.save()

        # clean up
        self.lines = []

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
