from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import Project
import sys, os


def loadDispositions(path):
    badPcodes = []
    for file in os.listdir(path):
        pcode, _ = file.split('.')
        pcode = pcode.replace('-', '', 1)
        try:
            project = Project.objects.get(pcode = pcode)
            dspFile = open(path + '/' + file, 'r')
            disposition = ''.join(dspFile.readlines())
            dspFile.close()
            project.disposition = disposition
            project.save()
            
        except Project.DoesNotExist:
            badPcodes.append(pcode)
    print len(badPcodes), 'not found in the DSS database.'
    print '\n'.join(badPcodes)

if __name__ == '__main__':
    path = sys.argv[1]
    loadDispositions(path)
