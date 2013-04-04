from LstPressures import LstPressures
from pht.models   import *
import numpy

class LstPrCompare:

    """
    A utility class for quickly comparing Green Bank LST Pressures for those reported
    by the NRAO PHT (Socorro's tool).
    Directions:
       * https://my.nrao.edu/pht/secure/index.xhtml -> https://my.nrao.edu/pht/secure/13B/GBT/v1.html?row=0
       * click 'View Pressure Plot'
       * Cut and paste the text box contents labeled 'Raw Session Pressure' into a local file.
       * Modify the args in this file's main function below, and run: python LstPrCompare
       * The resulting report can be used alone (see results at end), or one can diff this file with the 
         resulting *.formatted file to see details on diffs between Socorro and GB pressures.
    """

    def __init__(self, socFile=None, semester=None):

        self.semester = semester if semester is not None else '13B'
        self.socFile = socFile if socFile is not None else 'socPsV1.txt'
        self.socFrmtFile = self.socFile + '.formatted'
        self.gbLst = LstPressures()
        self.socPs = {} 
        self.gbPs = {} 
        self.diffs = {} 
        self.tolerance = 0.01
        self.gbNightFlagged = self.getNightTimeFlagSessions(self.semester)

    def getGbPressures(self, semester):
        self.gbLst.getPressures()
        ss = Session.objects.filter(semester__semester = semester).order_by('id')
        for s in ss:
            _, _, ps, _ = self.gbLst.pressuresBySession[s.__str__()]
            self.gbPs[s.id] = ps

    def getNightTimeFlagSessions(self, semester):
        ss = Session.objects.filter(semester__semester = semester).order_by('id')
        return [s for s in ss if s.flags.thermal_night or s.flags.optical_night or s.flags.rfi_night]

    def comparePressures(self):

        for gbId, gbPs in self.gbPs.items():
            # don't bother comparing sessions using night time flags
            if gbId not in [s.id for s in self.gbNightFlagged]:
               if self.socPs.has_key(gbId):
                   diffs = self.comparePressure(gbId, gbPs, gbId, self.socPs[gbId])
                   if len(diffs) > 0:
                       self.diffs[gbId] = diffs
    
        gbIds = set(self.gbPs.keys())                
        socIds = set(self.socPs.keys())                
        self.uniqueGbIds = gbIds.difference(socIds)
        self.uniqueSocIds = socIds.difference(gbIds)

    def comparePressure(self, gbId, gbPs, socId, socPs):

        # no problem if they are all within .01
        gbPs = numpy.array(gbPs)
        socPs = numpy.array(socPs)
        return [d for d in abs(gbPs - socPs) if d > self.tolerance]
        
    def formatSocFile(self):
        """
        Our file is produced by cutting and pasting the textbox in NRAO PHT's UI.
        So, the file has multiple rows all on ONE line, with each row having the
        format: (session id),pressure at LST 0,...,pressure at LST 23
        """
        
        f = open(self.socFile, 'r')
        lines = f.readlines()
        lines = lines[0]
        # introduce something that we can later split on
        lines = lines.replace('(', '\n(')
        ls = lines.replace(' ', '')
        # get rid of opening \n
        ls = ls[1:]
        lines = sorted(ls.split('\n'))
        f.close()

        # write it to a new file, in case we want
        # to diff it w/ a file of same format of GB pressures
        f = open(self.socFrmtFile, 'w')
        for l in lines:
            f.write(l + '\n')
        f.close()

        self.socPsLines = lines

    def parseSocPsLines(self, lines):
        "Convert formated strings to a dict mapping sessions to their pressures"
        for l in lines:
            self.parseSocPs(l)

    def parseSocPs(self, line):
        try:
            id, ps = line.split(')')
            id = int(id[1:])
            ps = ps[1:]
            ps = [float(p) for p in ps.split(',')]
            self.socPs[id] = ps
        except:
            pass

    def getName(self, sessionId):
        try:
            s = Session.objects.get(id = sessionId)
            return s.name
        except:
            return ''

    def report(self):

        self.gbLst.reportSocorroFormat(self.semester)
        print "Pipe this to a file and get rid of other lines if you want"
        print "to use tkdiff to compare the above to", self.socFrmtFile

        print ""
        print "Unique GB Sessions: ", [(self.getName(id), id) for id in self.uniqueGbIds]
        print "Unique Soc Sessions: ", [(self.getName(id), id) for id in self.uniqueSocIds]
        print "Sesisons with differences larger then %5.2f:" % self.tolerance
        for id, d in self.diffs.items():
            print self.getName(id), id, " : ", d
        print "Ignoring %d Sessions using Night Flags" % (len(self.gbNightFlagged))
        for s in self.gbNightFlagged:
            print "  ", s.name, s.id

    def compare(self):
        "Find notable differences between GB and Soc LST Pressures."
   
        # format and parse Socorro pressures
        self.formatSocFile()
        cmp.parseSocPsLines(cmp.socPsLines)
        # calculate gb pressures
        cmp.getGbPressures(self.semester)
        # now we can compare them
        self.comparePressures()

if __name__ == '__main__':

    f = 'socPsV2.txt'
    cmp = LstPrCompare(socFile = f, semester = '13B')
    cmp.compare()
    cmp.report()

