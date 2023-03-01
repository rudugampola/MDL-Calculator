from django.contrib import admin

# Register your models here.
from .models import Data

admin.site.register(Data)


class DataAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'analyte_name', 'cmp', 'cust_sample_id', 'lab_sample_id', 'matrix', 'matrix_desc', 'method_desc', 'result', 'result_units', 'run_date', 'sample_type', 'analyst', 'app_high', 'app_low', 'collection_site', 'collect_date', 'cust_id', 'cust_name', 'cust_workorder_id', 'dilution', 'formatted_idl', 'formatted_pql',
                    'formatted_rdl', 'formatted_result', 'hsn', 'idl', 'lab_workorder_id', 'location_seq', 'pql', 'prep_analyst', 'prep_run_date', 'prep_schedule_seq', 'profile_name', 'project_seq', 'rdl', 'receive_date', 'reqnbr', 'result_id', 'result_pos', 'sample_status', 'sample_type_desc', 'schedule_seq', 'text_result')
