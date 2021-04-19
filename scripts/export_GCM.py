# Exports temperature and precipitation projections for selected GCMs for a given time period
# Script written in Python 3.7

import __init__
import scripts.config as config
import numpy as np
import pandas as pd

# =======================================================================
# Config
start = pd.to_datetime('01-01-1984')
end = pd.to_datetime('12-31-2020')
models = ['access1.0_RCP45', 'access1.0_RCP85', 'access1.3_RCP85', 'bcc-csm1.1_RCP85',
          'canesm2_RCP85', 'ccsm4_RCP85', 'csiro-mk3.6.0_RCP85', 'fgoals-g2_RCP85',
          'gfdl-cm3_RCP85', 'giss-e2-h_RCP85', 'miroc5_RCP85', 'mri-cgcm3_RCP85', 'noresm1-m_RCP85']
selected_models = ['canesm2_RCP85', 'ccsm4_RCP85', 'giss-e2-h_RCP85', 'noresm1-m_RCP85']


# Convert model names to file-friendly format
model_names = [y.replace('-', '_') for y in [x.replace('.', '_') for x in selected_models]]

# Export GCM precipitation
wrf_dir = config.data_path / 'precip' / 'VIC_WRF_EllsworthCr'
wrf_file = 'flux_46.40625_-123.90625'
wrf_cols = ["YEAR", "MONTH", "DAY", "HOUR", "OUT_PREC", "OUT_PET_SHORT",
            "OUT_SWE", "OUT_EVAP", "OUT_RUNOFF", "OUT_BASEFLOW",
            "OUT_SOIL_MOIST0", "OUT_SOIL_MOIST1", "OUT_SOIL_MOIST2"]

for i, model in enumerate(selected_models):
    outfile_ppt = config.velma_data / 'precip' / '{}_{}_{}_ppt.csv'.format(model_names[i],
                                                                           abs(start.year) % 100,
                                                                           abs(end.year) % 100)
    arr = np.loadtxt(wrf_dir / model / 'sim_avg' / wrf_file)
    df = pd.DataFrame(arr, columns=wrf_cols)
    df.index = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
    daily_ppt = df.groupby(pd.Grouper(freq='d')).sum()['OUT_PREC']
    daily_ppt_sim = daily_ppt[(daily_ppt.index >= start) & (daily_ppt.index <= end)]
    daily_ppt_sim.to_csv(outfile_ppt, header=False, index=False)

# Export GCM temperature
forc_dir = config.data_path / 'precip' / 'WRF_frcs_EllsworthCr_forcings'
forc_file = 'forc_46.40625_-123.90625'
forc_cols = ['Year', 'Month', 'Day', 'Hour', 'Precip(mm)', 'Temp(C)',
             'Wind(m/s)', 'SWrad(W/m2)', 'LWrad(W/m2)', 'pressure(kPa)',
             'VaporPress(kPa)']

for i, model in enumerate(selected_models):
    outfile_temp = config.velma_data / 'temp' / '{}_{}_{}_temp.csv'.format(model_names[i],
                                                                           abs(start.year) % 100,
                                                                           abs(end.year) % 100)
    arr = np.loadtxt(forc_dir / model / forc_file)
    df = pd.DataFrame(arr, columns=forc_cols)
    df.index = pd.to_datetime(df[['Year', 'Month', 'Day']])
    daily_temp = df.groupby(pd.Grouper(freq='d')).mean()['Temp(C)']
    daily_temp_sim = daily_temp[(daily_temp.index >= start) & (daily_temp.index <= end)]
    daily_temp_sim.to_csv(outfile_temp, header=False, index=False)
