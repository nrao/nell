from django.core.management import setup_environ
import settings
setup_environ(settings)

from calculator.models import *

class WeatherValuesImport(object):

    def __init__(self, filename):
        f = open(filename)

        def processData(data):
            return [int(float(data[0]))] + map(float, data[1:])

        raw_data = [processData([i.replace('\n', '') for i in l.split(',') 
                                     if i != ' ' and i != ' \n']) for l in f.readlines()[1:]]
        self.data = [rd for rd in raw_data if len(rd) > 1]
        f.close()
        self.insertData()

    def insertData(self):
        for i, d in enumerate(self.data):
            wv = WeatherValues(*([i + 1] + d))
            wv.save()
            print wv
            

if __name__ == "__main__":
    wvi = WeatherValuesImport('calculator/utilities/SensCalcWeatherValues.csv')
