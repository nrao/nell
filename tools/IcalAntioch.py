from icalendar       import Calendar, Event, UTC
from datetime        import datetime, timedelta
from utilities.TimeAgent import dt2semester 

class IcalAntioch:

    """
    Creates a representative iCal in the specified file from a schedule
    that is a list of the Antioch string representations of Periods.
    This list can be easily created by cutting and pasting the periods
    listed in Antioch's simulation report 'simulation_<timestamp>.txt' under
    the heading 'Final Schedule'.
    """

    def __init__(self, inputFile, outputFile):
        self.cal = Calendar()
        self.cal.add('prodid', '-//My calendar product//mxm.dk//')
        self.cal.add('version', '2.0')
        self.cal.add('x-wr-calname;value=text', 'GBT Schedule')
        self.cal.add('summary', 'GBT Schedule')
        self.cal.add('calscale', 'GREGORIAN')
    
        self.inputFile = inputFile
        self.outputFile = outputFile

    def writeSchedule(self):
        "Parse the schedule input, and write it as an iCal."

        # read in the input
        f = open(self.inputFile, 'r')
        lines = f.readlines()
        f.close()
        id = 0
        for l in lines:
            dct = self.parsePeriod(l)
            # assign a unique id to this period
            dct['id'] = id
            id += 1
            # create the event in the calendar from the parsed period
            self.cal.add_component(self.createEvent(dct))

        # produce the output
        f = open(self.outputFile, 'wb')
        f.write(self.cal.as_string())
        f.close()        

    def parseSchedule(self):

        bandFilter = ['Q']
        print "filtering for bands: ", bandFilter

        # read in the input
        f = open(self.inputFile, 'r')
        lines = f.readlines()
        f.close()
        id = 0
        ps = []
        total = 0
        semTotals = {'06A' : 0
                   , '06B' : 0
                   , '06C' : 0}
        for l in lines:
            p = self.parsePeriod(l)
            if p['band'] in bandFilter:
                semester = dt2semester(p['start']) 
                semTotals[semester] += p['duration']
                total += p['duration']
                ps.append((p, semester, total, semTotals[semester]))
            #print p
        for p, sem, tl, st in ps:
            print "%9s at %s in %s for %d mins (%5.2f hrs) makes total of %d (%5.2f hrs) and for semester %d (%5.2f hrs)" % (p['sName'], p['start'], sem, p['duration'], p['duration']/60.0, tl, tl/60.0, st, st/60.0)
            

    def parsePeriod(self, pStr):
        """
        Given Antioch's string rep. of a Period, parse it.
        
        Example: 
        Period: 18 (0)  at 2006-02-01 00:00:00 for 420 (420) with score of 
        3.669943 from 2006-02-01 00:00:00 Scheduled  band: X  RA: 4.674547
        grade: 4.0
        """

        # TBF: this is not very robust - is completely dependent on Antioch's
        # Show function for a Period in Types.lhs

        # parse the string - this is not very robust, but we're are trying
        # to leverage what Antioch is already doing.
        parts = pStr.split(" ")

        # debug
        #for i, p in enumerate(parts):
        #    print i, p

        sName = parts[1]
        startDateStr = parts[5]
        startTimeStr = parts[6]
        durMins = int(parts[8])
        band = parts[20]

        start = datetime.strptime(startDateStr + " " + startTimeStr
                                , "%Y-%m-%d %H:%M:%S")
        dtstart = datetime(start.year, start.month, start.day,
                         start.hour, start.minute, start.second,
                         tzinfo = UTC)
        dtend = dtstart + timedelta(hours = durMins/60.0)     

        return dict(sName = sName
                  , dtstart = dtstart
                  , dtend = dtend
                  , start = start
                  , duration = durMins
                  , band = band)

    def createEvent(self, dct):
        "Creates an ical event from a dictionary representing the period."

        # exctract values
        id = dct["id"]
        sName = dct["sName"]
        dtstart = dct["dtstart"]
        dtend = dct["dtend"]
        band = dct["band"]

        # create event
        event = Event()
        event['uid'] = str(id) + "periodofgbtdss"
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('dtstamp', datetime.utcnow())
        event.add('summary', "%s at %s band (%s UTC)" %
                             (sName
                            , band
                            , dtstart.strftime("%Y/%m/%d %H:%M")
                             )
                 )            
        return event                             
        
