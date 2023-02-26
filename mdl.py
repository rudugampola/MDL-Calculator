import pandas as pd
from scipy.stats import t


def calculate_mdl(excel_file):
    # read in the Excel file
    df = pd.read_excel(excel_file)

    # filter out MDLREP and MDLBLK/MB types
    mdl_data = df[df['sample_type'].isin(['MDLREP', 'MDLBLK', 'MB'])]

    # group by analyte_name
    groups = mdl_data.groupby('analyte_name')

    # calculate MDLs and MDLb for each analyte
    mdls = {}
    mdlb = {}
    ver_mdl = {}

    for name, group in groups:
        reps = group[group['sample_type'] == 'MDLREP']
        blks = group[group['sample_type'].isin(['MDLBLK', 'MB'])]

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
                mdlb_a = mean_blk + t_val_blks * std_blk
            else:
                mdlb_a = blks['result'].max()
            mdls_a = std_rep * t_val_reps

            mdls[name] = mdls_a
            mdlb[name] = mdlb_a
            ver_mdl[name] = max(mdls_a, mdlb_a)
    return (mdls, mdlb, ver_mdl)


# Print MDLs and MDLbs for each analyte
for name, mdl in calculate_mdl('data.xlsx')[2].items():
    # Print formatted string
    print(f'{name}: {mdl}')
