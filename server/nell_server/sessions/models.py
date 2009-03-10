from django.db import models

class Sessions(models.Model):
    dummy = models.IntegerField(default = 0)

    class Meta:
        db_table = "sessions"

class Fields(models.Model):
    session = models.ForeignKey(Sessions)
    key     = models.CharField(max_length = 64)
    value   = models.CharField(max_length = 64)

    class Meta:
        db_table = "fields"

class ColumnHeaders(models.Model):
    name = models.CharField(max_length = 32)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        db_table = "columnheaders"

class Perspectives(models.Model):
    title = models.CharField(max_length = 32)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)
        db_table = "perspectives"

    headers = models.ManyToManyField(ColumnHeaders)

