import pandas as pd

files_collected_day1 = 33  # Number of ROIs collected each day
files_collected_day2 = 17
files_collected_day3 = 18

scans_per_roi = 400

scans_collected_day1 = files_collected_day1 * scans_per_roi
scans_collected_day2 = files_collected_day2 * scans_per_roi
scans_collected_day3 = files_collected_day3 * scans_per_roi

day_1 = [1 for _ in range(scans_collected_day1)]
day_2 = [2 for _ in range(scans_collected_day2)]
day_3 = [3 for _ in range(scans_collected_day3)]

days = day_1 + day_2 + day_3  # Making a list for the day column to indicate day scan was recorded

compounds = ['Caffeine', 'Emtricitabine', 'Propranolol', 'Fluconazole', 'Fluoxetine', 'Caffeine Isotope',
             'Emtricitabine Isotope', 'Propranolol Isotope', 'Fluconazole Isotope', 'Fluoxetine Isotope']


def configure_mma_file(file_path):
    """Takes the MMA file path as a csv file, puts it into the proper format and returns the resulting dataframe"""
    df = pd.read_csv(file_path)

    df = df.rename(columns={'195.0876\nMMA (ppm)': 'Caffeine MMA', '248.05\nMMA (ppm)': 'Emtricitabine MMA', '260.1645\nMMA (ppm)': 'Propranolol MMA',
                            '307.1113\nMMA (ppm)': 'Fluconazole MMA', '310.1413\nMMA (ppm)': 'Fluoxetine MMA', '196.091\nMMA (ppm)': 'Caffeine Isotope MMA', '250.0458\nMMA (ppm)': 'Emtricitabine Isotope MMA',
                            '261.1679\nMMA (ppm)': 'Propranolol Isotope MMA', '308.1147\nMMA (ppm)': 'Fluconazole Isotope MMA', '311.1447\nMMA (ppm)': 'Fluoxetine Isotope MMA', 'Abundance': 'Caffeine Abundance',
                            'Abundance.2': 'Emtricitabine Abundance', 'Abundance.4': 'Propranolol Abundance', 'Abundance.6': 'Fluconazole Abundance', 'Abundance.8': 'Fluoxetine Abundance', 'Abundance.1': 'Caffeine Isotope Abundance',
                            'Abundance.3': 'Emtricitabine Isotope Abundance', 'Abundance.5': 'Propranolol Isotope Abundance', 'Abundance.7': 'Fluconazole Isotope Abundance', 'Abundance.9': 'Fluoxetine Isotope Abundance',
                            'm/z': 'Caffeine m/z', 'm/z.2': 'Emtricitabine m/z', 'm/z.4': 'Propranolol m/z', 'm/z.6': 'Fluconazole m/z', 'm/z.8': 'Fluoxetine m/z',
                            'm/z.1': 'Caffeine Isotope m/z', 'm/z.3': 'Emtricitabine Isotope m/z', 'm/z.5': 'Propranolol Isotope m/z', 'm/z.7': 'Fluconazole Isotope m/z', 'm/z.9': 'Fluoxetine Isotope m/z',
                            'Num.\npoints': 'Caffeine Detected', 'Num.\npoints.1': 'Caffeine Isotope Detected', 'Num.\npoints.2': 'Emtricitabine Detected', 'Num.\npoints.3': 'Emtricitabine Isotope Detected',
                            'Num.\npoints.4': 'Propranolol Detected', 'Num.\npoints.5': 'Propranolol Isotope Detected', 'Num.\npoints.6': 'Fluconazole Detected', 'Num.\npoints.7': 'Fluconazole Isotope Detected',
                            'Num.\npoints.8': 'Fluoxetine Detected', 'Num.\npoints.9': 'Fluoxetine Isotope Detected'
                            }, errors='raise')

    df = df.drop(columns=['Local Scan', 'X', 'Z', ' ', ' .1', ' .2', ' .3', ' .4', ' .5', ' .6', ' .7', ' .8', ' .9', 'Scan'])

    df.insert(0, 'Scan', [x for x in range(1, len(df)+1)])
    df.insert(2, 'Day', days)

    for line in range(len(df)):  # Loops through the dataframe and seting isotope detection to NaN if monoisotopic peak not detected
        for compound in compounds[:5]:
            if df.loc[line, f'{compound} Detected'] == 0:
                df.loc[line, f'{compound} Isotope Detected'] = None

    return df


def combine_files(mma_df, sa_file, rsd_file):
    """Takes the edited MMA dataframe, the SA file path as an excel, and the RSD (autoQAQC) file as an excel file,
    combines them into a single dataframe and returns the combined dataframe"""
    roi_list = ['ROI'+str(roi) for roi in range(1, 69)]

    rsd_df = pd.read_excel(rsd_file, sheet_name='Tile RSD')
    rsd_df = rsd_df.set_axis(['m/z'] + roi_list, axis=1)
    rsd_df = rsd_df.set_axis(compounds[:5], axis=0)

    mma_df.insert(6, 'Caffeine RSD', None)
    mma_df.insert(15, 'Emtricitabine RSD', None)
    mma_df.insert(24, 'Propranolol RSD', None)
    mma_df.insert(33, 'Fluconazole RSD', None)
    mma_df.insert(42, 'Fluoxetine RSD', None)
    mma_df.insert(7, 'Caffeine SA', None)
    mma_df.insert(17, 'Emtricitabine SA', None)
    mma_df.insert(27, 'Propranolol SA', None)
    mma_df.insert(37, 'Fluconazole SA', None)
    mma_df.insert(47, 'Fluoxetine SA', None)

    multiplier = 0
    for file in range(1, int(len(mma_df)/400) + 1):  # Inputs the rsd value into the MMA dataframe, multiplier needed since the same value is repeated for scans in same ROI
        count = 0
        for line in range(len(mma_df)):
            if count <= 399:
                count += 1
                for compound in compounds[:5]:
                    mma_df.loc[line+multiplier, f'{compound} RSD'] = rsd_df.loc[f'{compound}', f'ROI{file}']
            else:
                multiplier += 400
                break

    sa_df = pd.read_excel(sa_file)
    for line in range(len(mma_df)):  # Inputs SA into MMA file for each scan, only if both peaks are detected
        for compound in compounds[:5]:
            if mma_df.loc[line, f'{compound} Isotope Detected'] < 0.5:
                mma_df.loc[line, f'{compound} SA'] = None
            else:
                mma_df.loc[line, f'{compound} SA'] = sa_df.loc[line, f'{compound} SA']
    return mma_df


def save_file(df, new_path):
    """Takes the final dataframe and the path for the new file as a csv and saves the file in file explorer"""
    df.to_csv(new_path, index=False)
    print(f'File saved to "{new_path}"!')


def qc_file_convert(mma_file, sa_file, rsd_file, new_file_path):
    mma_df = configure_mma_file(mma_file)
    combined_df = combine_files(mma_df, sa_file, rsd_file)
    save_file(combined_df, new_file_path)
