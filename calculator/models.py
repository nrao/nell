from django.db import models

from sesshuns import models as smodels

class Calc_Backend(models.Model):
    dss_backend = models.ForeignKey(smodels.Backend, null = True)
    name        = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    def getName(self):
        return self.dss_backend.name if self.dss_backend is not None else self.name

    class Meta:
        db_table = 'calculator_backend'

class Bandwidth(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_bandwidth'

class Beams(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_beams'

class SpectralWindows(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_spectral_windows'

class Polarization(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_polarization'

class Receiver(models.Model):
    name         = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    dss_receiver = models.ForeignKey(smodels.Receiver, null = True)
    band_low     = models.FloatField(null = True)
    band_hi      = models.FloatField(null = True)

    def __unicode__(self):
        return self.name

    def getName(self):
        if self.band_low is not None and self.band_hi is not None:
            return "%s (%s - %s GHz)" % (self.display_name, self.band_low, self.band_hi)
        else:
            return self.name

    class Meta:
        db_table = 'calculator_receiver'

class Switching(models.Model):
    name         = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_switching'

class Mode(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_mode'

class Integration(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_integration'

class Configuration(models.Model):
    backend      = models.ForeignKey(Calc_Backend)
    mode         = models.ForeignKey(Mode)
    receiver     = models.ForeignKey(Receiver)
    beams        = models.ForeignKey(Beams)
    polarization = models.ForeignKey(Polarization)
    windows      = models.ForeignKey(SpectralWindows)
    switching    = models.ForeignKey(Switching)
    bandwidth    = models.ForeignKey(Bandwidth)
    integration  = models.ForeignKey(Integration)

    class Meta:
        db_table = 'calculator_configuration'

    def getConfig(self):
        return {'backend'        : self.backend.name
              , 'mode'           : self.mode.name
              , 'receiver'       : self.receiver.name
              , 'beams'          : self.beams.name
              , 'polarization'   : self.polarization.name
              , 'windows'        : self.windows.name
              , 'switching_mode' : self.switching.name
              , 'bandwidth'      : self.bandwidth.name
              , 'integration'    : self.integration.name
              }

    def get(self, name):
        return self.getConfig()[name]

    configuration = property(getConfig)

class FrequencyResolution(models.Model):
    backend                 = models.ForeignKey(Calc_Backend)
    bandwidth               = models.FloatField(null = True)
    max_number_channels     = models.IntegerField()

    def __str__(self):
        return "%s (bw: %s, max_chan: %s)" % \
            (self.backend.name, self.bandwidth, self.max_number_channels)

    class Meta:
        db_table = 'calculator_frequency_resolution'

class WeatherValues(models.Model):

    frequency           = models.IntegerField()
    eta_dss             = models.FloatField()
    eta_surf            = models.FloatField()
    eta_track           = models.FloatField()
    t_atm               = models.FloatField()
    t_rcvr              = models.FloatField()
    tau0                = models.FloatField()
    est0                = models.FloatField()
    attenuation         = models.FloatField()
    eta_track_mustang   = models.FloatField(null = True)
    t_rcvr_mustang      = models.FloatField(null = True)
    est0_mustang        = models.FloatField(null = True)
    attenuation_mustang = models.FloatField(null = True)

    def __str__(self):
        return "%s %s" % (self.id, self.frequency)

    class Meta:
        db_table = 'calculator_weather_values'

def getName(hardware,id):
    Dict = {
       'backend'     : lambda id: Calc_Backend.objects.get(pk=id).getName(),
       'mode'        : lambda id: Mode.objects.get(pk=id).name,
       'receiver'    : lambda id: Receiver.objects.get(pk=id).getName(),
       'beams'       : lambda id: Beams.objects.get(pk=id).name,
       'polarization': lambda id: Polarization.objects.get(pk=id).name,
       'bandwidth'   : lambda id: Bandwidth.objects.get(pk=id).name,
       'windows'     : lambda id: SpectralWindows.objects.get(pk=id).name,
       'integration' : lambda id: Integration.objects.get(pk=id).name, 
       'switching'   : lambda id: Switching.objects.get(pk=id).name
       }
    return str(Dict[hardware](id))
    
