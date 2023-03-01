import pandas as pd
from scipy.stats import t
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Data


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def calculate_mdl(excel_file):
    # read in the Excel file
    df = pd.read_excel(excel_file)

    # filter out MDLREP and MDLBLK/MB types
    mdl_data = df[df['sample_type'].isin(['MDLREP', 'MDLBLK', 'MB'])]

    # group by analyte_name
    groups = mdl_data.groupby('analyte_name')
    filtered_reps = df[df['sample_type'] == 'MDLREP']
    filtered_blks = df[df['sample_type'].isin(['MDLBLK', 'MB'])]

    # calculate MDLs and MDLb for each analyte
    results = {}
    count = 1
    for name, group in groups:
        reps = group[group['sample_type'] == 'MDLREP']
        blks = group[group['sample_type'].isin(['MDLBLK', 'MB'])]
        # Get the formatted_pql value for the analyte
        cur_rl = group['formatted_pql'].iloc[0]
        cur_mdl = group['formatted_idl'].iloc[0]
        units = group['result_units'].iloc[0]
        criteria1 = False
        criteria2 = False
        adjust_mdl = False

        # Get the cas number for the analyte
        cas = group['cmp'].iloc[0]

        if not reps.empty and not blks.empty:
            std_rep = reps['result'].std()

            mean_blk = blks['result'].mean()
            std_blk = blks['result'].std()

            # calculate t-value appropriate for single-tailed 99th percentile
            t_val_reps = t.ppf(0.99, len(reps)-1)
            t_val_blks = t.ppf(0.99, len(blks)-1)

            # If number of data points is greater than or equal to 100
            # mdlb is calculated using the 99th percentile of the
            # t-distribution. If not mdlb is the highest value
            if len(blks) >= 100:
                # Round to 4 significant figures
                mdlb_a = round(mean_blk + t_val_blks * std_blk, 3)
            else:
                # Round to 4 significant figures
                mdlb_a = round(max(blks['result']), 3)
            mdls_a = round(std_rep * t_val_reps, 3)

            # Criteria 1: Is the Verified MDL within 0.5-2 times the Current MDL?
            if cur_mdl * 0.5 <= mdls_a <= cur_mdl * 2:
                criteria1 = True

            # Criteria 2: Are fewer than 3% of MB results above the current MDL?
            # Count number of MB results above the current MDL
            mb_greater_than_mdl = 0
            for index, row in blks.iterrows():
                if row['result'] > cur_mdl:
                    mb_greater_than_mdl += 1
            count_mb = len(blks)

            if mb_greater_than_mdl / count_mb < 0.03:
                criteria2 = True

            # The existing MDL may optionally be left unchanged if the answer to Criteria 1 and Criteria 2
            # are both "YES". Otherwise, adjust the MDL to the new verified MDL. This is based on the
            # guidelines of 40CFR 136 Appendix B, Section (4)(f).
            if criteria1 and criteria2:
                adjust_mdl = True

            results[name] = (mdlb_a, mdls_a, max(
                mdls_a, mdlb_a), cur_mdl, cur_rl, count, cas, units, criteria1, criteria2, adjust_mdl)
            count += 1

    # Date range for the data from run_date column, date_from is the latest date and date_to is the earliest date
    date_from = mdl_data['run_date'].min()
    date_to = mdl_data['run_date'].max()

    # Check if any field is empty, if so, set it to None
    for col in filtered_reps.select_dtypes(include=['object']):
        filtered_reps[col] = filtered_reps[col].apply(
            lambda x: x if x != '' else None)
    for col in filtered_blks.select_dtypes(include=['object']):
        filtered_blks[col] = filtered_blks[col].apply(
            lambda x: x if x != '' else None)

    results["metadata"] = (date_from, date_to, filtered_reps, filtered_blks)
    return results


def import_excel(request):
    # Import Excel data that user uploads
    if request.method == 'POST':

        if len(request.FILES) == 0:
            messages.error(request, 'No file was uploaded!')
            return HttpResponseRedirect(reverse("calculate:import_excel"))

        excel_file = request.FILES['excel_file']
        file_name = excel_file.name

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'File is not an Excel file!')
            return HttpResponseRedirect(reverse("calculate:import_excel"))

        print(bcolors.WARNING + "Importing Excel: " +
              file_name + bcolors.ENDC)

        mdl_result = calculate_mdl(excel_file)
        # Get date_from and date_to
        date_from = mdl_result["metadata"][0]
        date_to = mdl_result["metadata"][1]

        # Save REPS and BLKS data to Database
        reps = mdl_result["metadata"][2]
        blks = mdl_result["metadata"][3]

        # Save REPS and BLKS data to Database
        rep_count = 0
        blk_count = 0
        for index, row in reps.iterrows():
            rep = Data(
                file_name=file_name,
                analyte_name=row['analyte_name'],
                cmp=row['cmp'],
                cust_sample_id=row['cust_sample_id'],
                lab_sample_id=row['lab_sample_id'],
                matrix=row['matrix'],
                matrix_desc=row['matrix_desc'],
                method_desc=row['method_desc'],
                result=row['result'],
                result_units=row['result_units'],
                run_date=row['run_date'],
                sample_type=row['sample_type'],
                analyst=row['analyst'],
                app_high=row['app_high'],
                app_low=row['app_low'],
                collection_site=row['collection_site'],
                collect_date=row['collect_date'],
                cust_id=row['cust_id'],
                cust_name=row['cust_name'],
                cust_workorder_id=row['cust_workorder_id'],
                dilution=row['dilution'],
                formatted_idl=row['formatted_idl'],
                formatted_pql=row['formatted_pql'],
                formatted_rdl=row['formatted_rdl'],
                formatted_result=row['formatted_result'],
                hsn=row['hsn'],
                idl=row['idl'],
                lab_workorder_id=row['lab_workorder_id'],
                location_seq=row['location_seq'],
                pql=row['pql'],
                prep_analyst=row['prep_analyst'],
                prep_run_date=row['prep_run_date'],
                prep_schedule_seq=row['prep_schedule_seq'],
                profile_name=row['profile_name'],
                project_seq=row['project_seq'],
                rdl=row['rdl'],
                receive_date=row['receive_date'],
                reqnbr=row['reqnbr'],
                result_id=row['result_id'],
                result_pos=row['result_pos'],
                sample_status=row['sample_status'],
                sample_type_desc=row['sample_type_desc'],
                schedule_seq=row['schedule_seq'],
                text_result=row['text_result'],
            )
            rep_count += 1
            # print(bcolors.WARNING + str(rep) + bcolors.ENDC)
            rep.save()

        for index, row in blks.iterrows():
            blk = Data(
                file_name=file_name,
                analyte_name=row['analyte_name'],
                cmp=row['cmp'],
                cust_sample_id=row['cust_sample_id'],
                lab_sample_id=row['lab_sample_id'],
                matrix=row['matrix'],
                matrix_desc=row['matrix_desc'],
                method_desc=row['method_desc'],
                result=row['result'],
                result_units=row['result_units'],
                run_date=row['run_date'],
                sample_type=row['sample_type'],
                analyst=row['analyst'],
                app_high=row['app_high'],
                app_low=row['app_low'],
                collection_site=row['collection_site'],
                collect_date=row['collect_date'],
                cust_id=row['cust_id'],
                cust_name=row['cust_name'],
                cust_workorder_id=row['cust_workorder_id'],
                dilution=row['dilution'],
                formatted_idl=row['formatted_idl'],
                formatted_pql=row['formatted_pql'],
                formatted_rdl=row['formatted_rdl'],
                formatted_result=row['formatted_result'],
                hsn=row['hsn'],
                idl=row['idl'],
                lab_workorder_id=row['lab_workorder_id'],
                location_seq=row['location_seq'],
                pql=row['pql'],
                prep_analyst=row['prep_analyst'],
                prep_run_date=row['prep_run_date'],
                prep_schedule_seq=row['prep_schedule_seq'],
                profile_name=row['profile_name'],
                project_seq=row['project_seq'],
                rdl=row['rdl'],
                receive_date=row['receive_date'],
                reqnbr=row['reqnbr'],
                result_id=row['result_id'],
                result_pos=row['result_pos'],
                sample_status=row['sample_status'],
                sample_type_desc=row['sample_type_desc'],
                schedule_seq=row['schedule_seq'],
                text_result=row['text_result'],
            )
            blk_count += 1
            # print(bcolors.WARNING + str(blk) + bcolors.ENDC)
            blk.save()

        print(bcolors.OKGREEN + "Saved: " +
              str(rep_count) + " MDL Replicate Data Points." + bcolors.ENDC)
        print(bcolors.OKGREEN + "Saved: " +
              str(blk_count) + " MDL Blank Data Points." + bcolors.ENDC)

        # Remove "date" from mdl_result
        mdl_result.pop("metadata", None)

        return render(request, 'calculate/mdl_result.html', {'mdl_results': mdl_result, 'date_from': date_from, 'date_to': date_to, 'title': 'Calculate MDL', 'file_name': file_name})
    else:  # GET request
        return render(request, 'calculate/import_excel.html', {'title': 'Import MDL Data'})
