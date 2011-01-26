from datetime                            import datetime
from nell.utilities.database.DSSDatabase import DSSDatabase
from sesshuns.models                     import *

class DSSDatabase09B(DSSDatabase):
    """
    This class is responsible for adding any additional items to the database
    that is needed to run the DSS for this semester.
    NOTE: this really only exists to serve as legacy code.  We won't be 
    creating a database for 09B again (we're in 09C right now).  Don't
    expect this code to work.
    """

    def create(self):
        DSSDatabase.create(self, "09B")
        self.create_09B_conditions()
        print "09B DB created."

    def create_09B_conditions(self):
        semester = "09B"
        self.create_09B_rcvr_schedule()
        #self.set_fixed_projects()
        start = "20090601"
        end   = "20091001"
 
    def create_09B_rcvr_schedule(self):

        rcvrChanges = []

        # the first three days of 09B
        dt = datetime(2009, 5, 30, 0)
        rcvrs = ['L', 'C', 'X', 'S', 'RRI'] # TBF: bug w/ K band!
        rcvrChanges.append((dt, rcvrs))
     
        # June 2:
        # Ku Up, K down

        # A up, K down, U up (RRI down?)
        dt = datetime(2009, 6, 4, 16)
        rcvrs = ['L', 'C', 'X', 'S', 'Ku', '1070'] # TBF: which one is A band!
        rcvrChanges.append((dt, rcvrs))

        # A down, PF1*3 up
        dt = datetime(2009, 6, 10, 16)
        rcvrs = ['L', 'C', 'X', 'S', 'Ku', '342'] # TBF: which one is PF1*3 band!
        rcvrChanges.append((dt, rcvrs))

        # S up - cancelded!  it never came down 
        #dt = datetime(2009, 6, 11, 16)
        #rcvrs = ['L', 'C', 'X', 'Ku', '342', 'S'] 
        #rcvrChanges.append((dt, rcvrs))

        # PF1*3 down, PF1*8 up
        dt = datetime(2009, 6, 15, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down, PF1*3 up
        dt = datetime(2009, 7, 6, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*3 down, PF*8 up
        dt = datetime(2009, 7, 14, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down, RRI up
        dt = datetime(2009, 7, 22, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', 'RRI'] 
        rcvrChanges.append((dt, rcvrs))

        # RRI down, PF1*8 up 
        dt = datetime(2009, 7, 28, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # A down, PF1*3 up
        dt = datetime(2009, 8, 4, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*3 down, PF1*8 up
        dt = datetime(2009, 8, 11, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down RRI up
        dt = datetime(2009, 8, 26, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', 'RRI'] 
        rcvrChanges.append((dt, rcvrs))

        # RRI down, PF1*3 up
        dt = datetime(2009, 9, 2, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Sept 8 
        # PF1*3 down, PF1*4 up
        dt = datetime(2009, 9, 8, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '450'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*4 down, PF1*8 up
        dt = datetime(2009, 9, 16, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down A up
        dt = datetime(2009, 9, 28, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        for dt, rcvrs in rcvrChanges:
            for rcvr in rcvrs:
                r = first(Receiver.objects.filter(abbreviation = rcvr))
                rs = Receiver_Schedule(receiver = r, start_date = dt)
                rs.save()
                #print rs

    def create_maintenance_opts(self):
        """
        Create the summer maintenance dates needed for 09B.
        These aren't being transferred by Carl, so we must create them:
        June 1 - Sep. 30: Mon - Thr, starting at 7 AM for 10.5 Hrs
        Holiday Weekends: Mon - Thr, starting at 8 AM for 8.5  Hrs
        NRAO Holidays 09: July 3, Sep 7
        There will be some fixed sessions (VLBI, Radar) that will conflict
        with these - they should be managed by hand.
        """

        s = first(Sesshun.objects.filter(name = "Fixed Summer Maintenance"))

        # now create entries in Windows and Opportunities that can be
        # translated into Periods for this fixed session

        # some maintenance days can't be scheduled normaly because of 
        # radar runs and the like
        conflicts = [ datetime(2009, 6,  9, 11) ]
                    #, datetime(2009, 6, 16, 11)
                    #]

        # what weeks have NRAO holidays in them?
        # July 3, Friday!
        holidayWeek1 = [datetime(2009, 6, 29) + timedelta(days=i) for i in range(4)]
        holidayWeek2 = [datetime(2009, 9,  7) + timedelta(days=i) for i in range(4)]
        holidayWeeks = holidayWeek1
        holidayWeeks.extend(holidayWeek2)

        # first, loop through weeks
        for week in range(22): #18):
            # then loop through Mon - Thrs
            for day in range(4): 
                # TBF: what time zone are we using?  See what happens to these
                # times when we load them up in Antioch ...
                dt = semesterStart + timedelta(days = (week*7) + day)
                # do we need to adjust for NRAO holiday?
                if dt in holidayWeeks:
                    # holiday week
                    # watch for that pesky labor day - it falls on a Monday
                    start = dt + timedelta(seconds = 12 * 60 * 60) #12 == 8 AM
                    if start == datetime(2009, 9, 7):
                        # schedule monday's on friday!
                        start = datetime(2009, 9, 11)
                    dur = 8.5 # hrs
                else:
                    # normal week
                    start = dt + timedelta(seconds = 11 * 60 * 60) #11 == 7 AM ET

                    dur = 10.5 # hrs

                # create the table entries
                # don't do this past Sep 30!
                if start <= semesterEnd:
                    if start not in conflicts:
                        w = Window( session = s, required = True)
                        w.save()
                        o = Opportunity( window     = w
                                   , start_time = start
                                   , duration   = dur
                                   )
                        o.save()               
                        # create TP's for the first two weeks!
                        if start < scheduledUpTo:
                            period = Period( session = s
                                           , start_time = start
                                           , duration = dur
                                           , backup = False )
                    else:
                        # we have conflicts!
                        if start == datetime(2009, 6, 9, 11):
                            #dt1 = start + timedelta(seconds = int(7.75 * 60 * 60))
                            dt1 = start
                            durHrs1 = 6.75
                            dt2 = start + timedelta(seconds = int(8 * 60 * 60))
                            durHrs2 = 2.5
                        #elif start == datetime(2009, 6, 16, 11): 
                        #    dt1 = start
                        #    durHrs1 = 6.00
                        #    dt2 = start + timedelta(seconds = int(7.5 * 60 * 60))
                        #    durHrs2 = 3.0 
                        else:
                            raise "SHIT!"
                        for dt, duration in [(dt1,durHrs1),(dt2,durHrs2)]:
                            w = Window( session = s, required = True)
                            w.save()
                            o = Opportunity( window     = w
                               , start_time = dt
                               , duration   = duration
                               )
                            o.save()           
                            # create TP's for the first two weeks!
                            if start < scheduledUpTo:
                                period = Period( session = s
                                           , start_time = start
                                           , duration = dur 
                                           , backup = False )

    def create_other_fixed_opts(self):

        s = first(Sesshun.objects.fitler(name = "testing").all())
        print "session: ", s

        # project, session, date time, dur (Hrs)
        # dates are in UT (+4 from ET)
        fixed = [
         ("GBT08A-073", "GBT08A-073-01", datetime(2009, 6, 1, 23, 30), 1.0)
        ,("Tests", "testing", datetime(2009, 6, 2, 0, 30), 3.5) # RRI
        ,("Tests", "testing", datetime(2009, 6, 2, 4, 0), 7.0) # Point B
        ,("Tests", "testing", datetime(2009, 6, 2, 21, 30), 1.5) # RCO U
        ,("Tests", "testing", datetime(2009, 6, 3, 4, 0), 3.5) # GUPPI
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 3, 7, 30), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 3, 21, 30), 4.0) #RRI
        ,("Tests", "testing", datetime(2009, 6, 4, 21, 30), 1.5) # RCO*A
        ,("Tests", "testing", datetime(2009, 6, 6, 12, 30), 4.0) # GUPPI
        ,("BB240", "BB240-02", datetime(2009, 6, 6, 17, 30), 8.5)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 9, 17, 45), 1.25)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 10, 7, 0), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 10, 21, 30), 1.5) # RCO*3
        ,("GBT09B-044", "GBT09B-044-01", datetime(2009, 6, 11, 5, 0), 6.0)
        ,("GBT08C-014", "GBT08C-014-01", datetime(2009, 6, 12, 6, 45), 0.75)
        ,("GBT08C-023", "GBT08C-023-01", datetime(2009, 6, 12, 7, 30), 3.75)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 13, 17, 30), 1.25)
        ,("BB240", "BB240-01", datetime(2009, 6, 14, 2, 0), 8.5)
        ,("Tests", "testing", datetime(2009, 6, 14, 13, 0), 4.0) # GUPPI
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 14, 17, 30), 1.25)
        ,("GBT08A-037", "GBT08A-037-01", datetime(2009, 6, 15, 0, 30), 4.5)
        ,("GBT09B-006", "GBT09B-006-01", datetime(2009, 6, 15, 5, 0), 1.5)
        ,("Tests", "testing", datetime(2009, 6, 15, 21, 30), 1.5) # RCO*8
        ,("GBT09B-028", "GBT09B-028-01", datetime(2009, 6, 16, 1, 30), 5.5)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 17, 4, 45), 1.75)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 17, 6, 30), 2.0)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 18, 4, 45), 1.75)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 19, 4, 45), 1.75)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 19, 18, 0), 1.25)
        ,("Tests", "testing", datetime(2009, 6, 19, 19, 15), 4.0) # GUPPI
        ,("BB240", "BB240-03", datetime(2009, 6, 20, 3, 30), 8.5)
        ,("GBT08B-025", "GBT08B-025-01", datetime(2009, 6, 20, 16, 45), 5.5)
        ,("Tests", "testing", datetime(2009, 6, 21, 4, 0), 2.0) # Q HP
        ,("GBT08C-023", "GBT08C-023-02", datetime(2009, 6, 21, 6, 0), 1.0)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 21, 17, 0), 1.0)
        ,("GBT07A-087", "GBT07A-087-01", datetime(2009, 6, 21, 21, 30), 7.5)
        ,("GBT07A-087", "GBT07A-087-02", datetime(2009, 6, 22, 21, 30), 7.5)
        ,("Tests", "testing", datetime(2009, 6, 23, 5, 0), 4.0) # M&C Integ
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 23, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 24, 0, 30), 2.5)
        ,("GBT08C-014", "GBT08C-014-01", datetime(2009, 6, 24, 5, 15), 0.75)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 24, 6, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 24, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 25, 0, 30), 2.5)
        ,("Tests", "testing", datetime(2009, 6, 25, 5, 0), 4.0) # M&C Integ
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 25, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 26, 0, 30), 2.5)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 26, 4, 45), 1.75)
        ,("GBT08C-023", "GBT08C-023-01", datetime(2009, 6, 26, 8, 15), 3.75)
        ,("Tests", "testing", datetime(2009, 6, 26, 13, 0), 4.0) # GUPPI
        ,("BB240", "BB240-04", datetime(2009, 6, 27, 0, 30), 8.5)
        ,("Tests", "testing", datetime(2009, 6, 27, 11, 15), 6.0) # M&C Integ
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 27, 17, 15), 1.25)
        ,("BM305", "BM305-01", datetime(2009, 6, 27, 21, 15), 8.5)
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 28, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 29, 0, 30), 2.5)
        ,("Tests", "testing", datetime(2009, 6, 29, 21, 30), 4.0) # M&C Integ
        ,("GBT09B-028", "GBT09B-028-01", datetime(2009, 6, 30, 4, 0), 2.0)
        ,("GBT09B-028", "GBT09B-028-01", datetime(2009, 7, 1, 4, 0), 1.75)
        ,("GLST011217", "GLST011217-01", datetime(2009, 7, 1, 5, 45), 1.75)
        ,("Tests", "testing", datetime(2009, 7, 1, 20, 30), 3.0) # OOF
        #("Project Name", "" unless "testing", start time (UT), Len)
        ]

        for pName, sName, start, durHrs in fixed:
            #p = first(Project.objects.filter( name = pName )
            print pName, sName, start, durHrs
            s = first(Sesshun.objects.filter( name = sName ))
            print "window for session: ", s
            
            win = Window(session = s, required = True)
            win.save()
            op = Opportunity(window = win
                           , start_time = start 
                           , duration = durHrs
                           )
            op.save()
            print op

    def create_history_09B(self):
        "The first few weeks of 09B have already been scheduled."

        fixed = [
         ("GBT08A-073", "GBT08A-073-01", datetime(2009, 6, 1, 23, 30), 1.0)
        ,("Tests", "testing", datetime(2009, 6, 2, 0, 30), 3.5) # RRI
        ,("Tests", "testing", datetime(2009, 6, 2, 4, 0), 7.0) # Point B
        ,("Tests", "testing", datetime(2009, 6, 2, 21, 30), 1.5) # RCO U
        ,("Tests", "testing", datetime(2009, 6, 3, 4, 0), 3.5) # GUPPI
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 3, 7, 30), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 3, 21, 30), 4.0) #RRI
        ,("Tests", "testing", datetime(2009, 6, 4, 21, 30), 1.5) # RCO*A
        ,("Tests", "testing", datetime(2009, 6, 6, 12, 30), 4.0) # GUPPI
        ,("BB240", "BB240-02", datetime(2009, 6, 6, 17, 30), 8.5)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 9, 17, 45), 1.25)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 10, 7, 0), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 10, 21, 30), 1.5) # RCO*3
        ,("GBT09B-044", "GBT09B-044-01", datetime(2009, 6, 11, 5, 0), 6.0)
        ,("GBT08C-014", "GBT08C-014-01", datetime(2009, 6, 12, 6, 45), 0.75)
        ,("GBT08C-023", "GBT08C-023-01", datetime(2009, 6, 12, 7, 30), 3.75)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 13, 17, 30), 1.25)
        ,("BB240", "BB240-01", datetime(2009, 6, 14, 2, 0), 8.5)
        ,("Tests", "testing", datetime(2009, 6, 14, 13, 0), 4.0) # GUPPI
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 14, 17, 30), 1.25)
        ]

        for pName, sName, start, durHrs in fixed:
            #p = first(Project.objects.filter( name = pName )
            print pName, sName, start, durHrs
            s = first(Sesshun.objects.filter( name = sName ))
            print "period for session: ", s
            p = Period( session = s
                      , start = start
                      , duration = durHrs
                      , backup = False )
            p.save()        

    def set_fixed_projects(self):
        "temporary fix until carl's DB gets these as fixed."

        stype    = first(Session_Type.objects.filter(type = "fixed"))
        pcodes = ["GBT09A-092"
                , "GBT09A-093"
                , "GBT09A-094"
                , "GBT09A-096"
                , "GBT07C-013"
                , "GBT09B-006"
                , "GBT09B-031"
                , "GBT09B-029"]            
        for pcode in pcodes:
            p = first(Project.objects.filter(pcode = pcode).all())
            print p
            ss = p.sesshun_set.all()
            for s in ss:
                s.session_type = stype
                s.save()

    # TBF: this was really part of DSSPrime2DSS and won't work here ...

    def transfer_project_blackouts_09B(self):
        "Only needed for scheduling 09B: project blackouts will then go away."

        query = "SELECT * from blackouts"
        self.cursor.execute(query)
        blackoutRows = self.cursor.fetchall()

        for row in blackoutRows:
            start       = row[1]
            end         = row[2]
            description = row[3]
            pkey        = row[5]
            pcodes      = row[6]

            # the people key and the pcodes must be matched to the right
            # people and projects
            query = "SELECT * FROM authors WHERE peoplekey = %d" % pkey
            self.cursor.execute(query)
            authors = self.cursor.fetchall()
            if len(authors) > 0:
                authorRow = list(authors[0])
                # we need to pop off the project id in order to be able to
                # use the create_user method
                p_id = authorRow.pop(1) 
                u = self.create_user(authorRow)
            else:
                # TBF: the fact that this is happening seems like a big
                # bug to me, but Carl just left us for a month. WTF
                #print "WARNING: peoplekey in blackouts ~ in authors: ", pkey
                u = None

            # now what different projects is this for?
            pcodeList = pcodes.split(",")
            for pcode in pcodes.split(","):
                # each project gets its own project blackout!
                p = first(Project.objects.filter(pcode = pcode.strip()))
                if p is not None:
                    pb = Project_Blackout_09B(
                        project     = p
                      , requester   = u
                      , start_date  = start
                      , end_date    = end
                      , description = description
                    )
                    pb.save()

                
