from django.contrib import admin

# Register your models here.
from .models import Analyte


class AnalyteAdmin(admin.ModelAdmin):
    model = Analyte
    list_display = ("analyte_name", "cas", "mdl_cal_spike", "mdl_cal_blank",
                    "mdl_verified", "current_mdl", "current_rl", "units")
