import matplotlib.pyplot as plt
from datetime import datetime
import os

def usage(directory):
    totals  = []
    results = []
    dates   = []
    for log in os.listdir(directory):
        if 'access' in log:
            o       = os.popen('cat ' + directory + '/' + log + ' | grep calculator | wc -l')
            total   = o.readline().replace('/n', '')
            o.close()
            o       = os.popen('cat ' + directory + '/' + log + ' | grep "/calculator/results" | wc -l')
            result  = o.readline().replace('/n', '')
            o.close()

            date = log.split('.')[0]
            dt = datetime.strptime(date, '%Y-%m-%d')
            if dt.date != datetime.now().date:
                totals.append(int(total))
                results.append(int(result))
                dates.append(dt)
                print '%s\t%s\t%s' % (date, int(total), int(result))
    return totals, results, dates

print 'log file\t\tTotal\tResults'
totals, results, dates = usage('/home/dss2.gb.nrao.edu/logs/2013/01')
ts, rs, dts            = usage('/home/dss2.gb.nrao.edu/logs/2013/02')
totals.extend(ts)
results.extend(rs)
dates.extend(dts)
accum = []
acount = 0
for r in results:
    acount += r
    accum.append(acount)

plt.figure(1)
#plt.title('Sensitivity Calculator Usage: Jan - Feb 1 2012')
plt.subplot(211)
#plt.plot(totals, 'bo-')
plt.plot(accum, 'bo-')
plt.ylabel('Accumulative # of results')
plt.xlabel('days')

plt.subplot(212)
plt.plot(results, 'go-')
plt.ylabel('# of results')
plt.xlabel('days')
#plt.xticks(range(len(dates)), [d.strftime('%Y-%m-%d') for d in dates])
plt.show()
