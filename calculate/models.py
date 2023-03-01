from django.db import models


class Data(models.Model):
    file_name = models.CharField(max_length=255)
    analyte_name = models.CharField(max_length=255)
    cmp = models.CharField(max_length=255)
    cust_sample_id = models.CharField(max_length=255)
    lab_sample_id = models.CharField(max_length=255)
    matrix = models.CharField(max_length=255)
    matrix_desc = models.CharField(max_length=255)
    method_desc = models.CharField(max_length=255)
    result = models.FloatField(null=True)
    result_units = models.CharField(max_length=255)
    run_date = models.DateTimeField(null=True, blank=True)
    sample_type = models.CharField(max_length=255)
    analyst = models.CharField(max_length=255)
    app_high = models.FloatField(null=True)
    app_low = models.FloatField(null=True)
    collection_site = models.CharField(max_length=255)
    collect_date = models.CharField(max_length=255)
    cust_id = models.CharField(max_length=255)
    cust_name = models.CharField(max_length=255)
    cust_workorder_id = models.CharField(max_length=255)
    dilution = models.CharField(max_length=255)
    formatted_idl = models.FloatField(null=True)
    formatted_pql = models.FloatField(null=True)
    formatted_rdl = models.FloatField(null=True)
    formatted_result = models.CharField(max_length=255)
    hsn = models.CharField(max_length=255)
    idl = models.FloatField(null=True)
    lab_workorder_id = models.CharField(max_length=255)
    location_seq = models.CharField(max_length=255)
    pql = models.FloatField(null=True)
    prep_analyst = models.CharField(max_length=255)
    prep_run_date = models.DateTimeField(null=True, blank=True)
    prep_schedule_seq = models.CharField(max_length=255)
    profile_name = models.CharField(max_length=255)
    project_seq = models.CharField(max_length=255)
    rdl = models.FloatField(null=True)
    receive_date = models.DateTimeField(null=True, blank=True)
    reqnbr = models.CharField(max_length=255)
    result_id = models.CharField(max_length=255)
    result_pos = models.CharField(max_length=255)
    sample_status = models.CharField(max_length=255)
    sample_type_desc = models.CharField(max_length=255)
    schedule_seq = models.CharField(max_length=255)
    text_result = models.TextField()

    def __str__(self):
        return self.analyte_name
