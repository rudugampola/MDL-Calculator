from django.db import models

# Create your models here.


class Analyte(models.Model):
    analyte_name = models.CharField(max_length=64, blank=True)
    cas = models.CharField(max_length=64, blank=True)
    mdl_cal_spike = models.FloatField()
    mdl_cal_blank = models.FloatField()
    mdl_verified = models.FloatField()
    current_mdl = models.FloatField()
    current_rl = models.FloatField()
    units = models.CharField(max_length=64, blank=True)
