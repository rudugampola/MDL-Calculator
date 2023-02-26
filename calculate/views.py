import pandas as pd
from scipy.stats import t
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

# from .models import Analyte


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

    # calculate MDLs and MDLb for each analyte
    results = {}
    count = 1
    for name, group in groups:
        reps = group[group['sample_type'] == 'MDLREP']
        blks = group[group['sample_type'].isin(['MDLBLK', 'MB'])]
        # Get the formatted_pql value for the analyte
        cur_rl = group['formatted_pql'].iloc[0]
        cur_mdl = group['formatted_idl'].iloc[0]

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

            results[name] = (mdlb_a, mdls_a, max(
                mdls_a, mdlb_a), cur_mdl, cur_rl, count, cas)
            count += 1

    # Date range for the data from run_date column, date_from is the latest date and date_to is the earliest date
    date_from = mdl_data['run_date'].min()
    date_to = mdl_data['run_date'].max()

    results["date"] = (date_from, date_to)
    return results


def import_excel(request):
    # Import Excel data that user uploads
    if request.method == 'POST':

        if len(request.FILES) == 0:
            messages.error(request, 'No file was uploaded!')
            return HttpResponseRedirect(reverse("calculate:import_excel"))

        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'File is not an Excel file!')
            return HttpResponseRedirect(reverse("calculate:import_excel"))

        print(bcolors.WARNING + "Importing Excel: " +
              excel_file.name + bcolors.ENDC)

        mdl_result = calculate_mdl(excel_file)
        # Get date_from and date_to
        date_from = mdl_result["date"][0]
        date_to = mdl_result["date"][1]

        # Remove "date" from mdl_result
        mdl_result.pop("date", None)

        return render(request, 'calculate/mdl_result.html', {'mdl_results': mdl_result, 'date_from': date_from, 'date_to': date_to, 'title': 'Calculate MDL'})
    else:  # GET request
        return render(request, 'calculate/import_excel.html', {'title': 'Import MDL Data'})
