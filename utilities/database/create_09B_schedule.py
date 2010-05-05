from nell.utilities.database.DSSPrime2DSS import DSSPrime2DSS
from nell.utilities.database.DSS2DSSPrime import DSS2DSSPrime
from nell.tools.DBReporter                import DBReporter 
from nell.tools.IcalMap                   import IcalMap

print "Instructions for how to do this manually are at: "
print "http://wiki.gb.nrao.edu/bin/view/Software/HowToSchedule09B"
print ""

r = raw_input("First transfer Carl's DB to dss_prime.  Do this manually, then hit enter. ")
r = raw_input("double check settings.py DBNAME, rebootDB, then hit enter to start transfering data from dss_prime: ")

# TBF: the below
t = DSSPrime2DSS() 
t.create_09B_database()  
print "created 09B database!"

response = raw_input("See any errors in output?  If not, continue: ")

r = DBReporter(filename = "dbReportPreSim.txt")
r.report()
print "Report written: dbReportPreSim.txt. Ready?: "

r = raw_input("Make sure periods table in DB for sims is empty before simulating.: ")

response = raw_input("Run Simulation, then hit enter to produce new report: ")

r = DBReporter(filename = "dbReportPostSim.txt")
r.report()

print "Report written: dbReportPostSim.txt. Ready?: "

i = IcalMap()
i.writeSchedule("schedule09B.ics")
r = raw_input("ical written to: schedule09B.  hit enter to continue: ")

# transfer over periods to dss_prime
r = raw_input("Make sure periods table in dss_prime has been TRUNCATED!: ")
r = raw_input("Press enter to transfer simulation periods to dss_prime DB: ")

t2 = DSS2DSSPrime()
t2.transfer()

print "Periods transferred to dss_prime!"

print "09B schedule complete!"
print "Don't forget to forward these results to the interested parties!"


