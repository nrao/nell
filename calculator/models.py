from django.db import models

from sesshuns import models as smodels

class Calc_Backend(models.Model):
    name = models.CharField(max_length=200)
    k1   = models.FloatField()
    k2   = models.FloatField()

    def __unicode__(self):
        return self.name

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

class Cc(models.Model):
    topo_freq = models.FloatField()
    cc        = models.FloatField()

    class Meta:
        db_table = 'calculator_cc'

class Efficiency(models.Model):
    topo_freq            = models.FloatField()
    efficiency_atm_a     = models.FloatField()
    efficiency_track_a   = models.FloatField()
    efficiency_surf_a    = models.FloatField()
    efficiency_atm_b     = models.FloatField()
    efficiency_track_b   = models.FloatField()
    efficiency_surf_b    = models.FloatField()
    efficiency_atm_c     = models.FloatField()
    efficiency_track_c   = models.FloatField()
    efficiency_surf_c    = models.FloatField()
    efficiency_atm_all   = models.FloatField()
    efficiency_track_all = models.FloatField()
    efficiency_surf_all  = models.FloatField()

    class Meta:
        db_table = 'calculator_efficiency'

class FrequencyResolution(models.Model):
    backend                 = models.ForeignKey(Calc_Backend)
    bandwidth               = models.FloatField(null = True)
    max_number_channels     = models.IntegerField()

    def __str__(self):
        return "%s (bw: %s, max_chan: %s)" % \
            (self.backend.name, self.bandwidth, self.max_number_channels)

    class Meta:
        db_table = 'calculator_frequency_resolution'

class Integration(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'calculator_integration'

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
    dss_receiver = models.ForeignKey(smodels.Receiver, null = True)
    band_low     = models.FloatField(null = True)
    band_hi      = models.FloatField(null = True)

    def __unicode__(self):
        return self.name

    def getName(self):
        if self.band_low is not None and self.band_hi is not None:
            return "%s (%s - %s)" % (self.name, self.band_low, self.band_hi)
        else:
            return self.name

    class Meta:
        db_table = 'calculator_receiver'

class Switching(models.Model):
    name = models.CharField(max_length=200)

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

class NOverlap(models.Model):
    backend               = models.CharField(max_length=200)
    n_overlap             = models.FloatField()
    level                 = models.FloatField()
    sensitivity_n_overlap = models.FloatField()

    class Meta:
        db_table = 'calculator_n_overlap'

class Temperatures(models.Model):
    topo_freq = models.FloatField()
    tau_0_a   = models.FloatField()
    tau_0_b   = models.FloatField()
    tau_0_c   = models.FloatField()
    tau_0_all = models.FloatField()
    tatm_a    = models.FloatField(db_column=u'tATM_a')
    tatm_b    = models.FloatField(db_column=u'tATM_b')
    tatm_c    = models.FloatField(db_column=u'tATM_c') 
    tatm_all  = models.FloatField(db_column=u'tATM_all') 
    trcvr     = models.FloatField(db_column=u'tRCVR') 

    class Meta:
        db_table = 'calculator_temperatures'

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

def getName(hardware,id):
    Dict = {
       'backend'     : lambda id: Calc_Backend.objects.get(pk=id).name,
       'mode'        : lambda id: Mode.objects.get(pk=id).name,
       'receiver'    : lambda id: Receiver.objects.get(pk=id).getName(),
       'beams'       : lambda id: Beams.objects.get(pk=id).name,
       'polarization': lambda id: Polarization.objects.get(pk=id).name,
       'bandwidth'   : lambda id: Bandwidth.objects.get(pk=id).name,
       'windows'     : lambda id: SpectralWindows.objects.get(pk=id).name,
       'integration' : lambda id: Integration.objects.get(pk=id).name, 
       'switching'   : lambda id: Switching.objects.get(pk=id).name
       }
    #print "getting "+hardware+" with id "+str(id)
    return str(Dict[hardware](id))
    
