# This script takes VIC WRF files supplied by the University of Washington Climate Impacts Group
# and exports precipitation and temperature averaged from the multiple climate simulation runs.
# wrf_dir and frc_dir are directories where the projections (with temperature) and forcings (with precipitation)
# files are located.
# Written in Python 3.7

import __init__
import scripts.config as config
import numpy as np
import pandas as pd
import os

# =======================================================================
# Load raw VIC WRF climate files

wrf_dir = config.data_path / 'precip' / 'VIC_WRF_EllsworthCr'

wrf_file = 'flux_46.40625_-123.90625'
wrf_cols = ["YEAR", "MONTH", "DAY", "HOUR", "OUT_PREC", "OUT_PET_SHORT",
            "OUT_SWE", "OUT_EVAP", "OUT_RUNOFF", "OUT_BASEFLOW",
            "OUT_SOIL_MOIST0", "OUT_SOIL_MOIST1", "OUT_SOIL_MOIST2"]

for sim_dir in os.listdir(wrf_dir):
    runs = os.listdir(wrf_dir / sim_dir)
    try:
        runs.remove('sim_avg')
    except ValueError:
        pass
    arrs = []
    for run in runs:
        arr = np.loadtxt(wrf_dir / sim_dir / run / wrf_file)
        arrs.append(arr)
    stack = np.dstack(arrs)
    averaged = np.mean(stack, axis=2)
    out_dir = wrf_dir / sim_dir / 'sim_avg'
    try:
        out_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    np.savetxt(out_dir / '{}.gz'.format(wrf_file), averaged)

# =======================================================================
# Save averaged temp file
forc_dir = config.data_path / 'precip' / 'WRF_frcs_EllsworthCr_forcings'

forc_file = 'forc_46.40625_-123.90625'
forc_cols = ['Year', 'Month', 'Day', 'Hour', 'Precip(mm)', 'Temp(C)',
             'Wind(m/s)', 'SWrad(W/m2)', 'LWrad(W/m2)', 'pressure(kPa)',
             'VaporPress(kPa)']

cols = ['Temp(C)']
inds = [forc_cols.index(x) for x in cols]
arrs = []
sim_dirs = []
for sim_dir in os.listdir(forc_dir):
    if sim_dir == 'pnnl_historical':
        continue
    sim_dirs.append(sim_dir)
    arr = np.loadtxt(forc_dir / sim_dir / forc_file)
    arrs.append(arr[:, inds])
stack = np.column_stack(arrs)
proj_sims_temp = pd.DataFrame(stack, columns=sim_dirs)
date_arr = pd.DataFrame(arr, columns=forc_cols)
proj_sims_temp = np.column_stack([date_arr[['Year', 'Month', 'Day']], stack])

# Export just averaged temp to speed up imports in the future
gcm_avg_forc_dir = forc_dir / 'sim_avg'
try:
    gcm_avg_forc_dir.mkdir(parents=True)
except FileExistsError:
    pass

np.savetxt(gcm_avg_forc_dir / 'sim_avg_temp.gz', proj_sims_temp)

# =======================================================================
# Save averaged precip file

wrf_file = 'flux_46.40625_-123.90625'
wrf_cols = ["YEAR", "MONTH", "DAY", "HOUR", "OUT_PREC", "OUT_PET_SHORT",
            "OUT_SWE", "OUT_EVAP", "OUT_RUNOFF", "OUT_BASEFLOW",
            "OUT_SOIL_MOIST0", "OUT_SOIL_MOIST1", "OUT_SOIL_MOIST2"]

cols = ['OUT_PREC']
inds = [wrf_cols.index(x) for x in cols]
arrs = []
sim_dirs = []
for sim_dir in os.listdir(wrf_dir):
    if sim_dir == 'pnnl_historical':
        continue
    sim_dirs.append(sim_dir)
    arr = np.loadtxt(wrf_dir / sim_dir / 'sim_avg' / '{}.gz'.format(wrf_file))
    arrs.append(arr[:, inds])
stack = np.column_stack(arrs)
proj_sims_ppt = pd.DataFrame(stack, columns=sim_dirs)
date_arr = pd.DataFrame(arr, columns=wrf_cols)
proj_sims_ppt = np.column_stack([date_arr[['YEAR', 'MONTH', 'DAY']], stack])

# Export just averaged temp to speed up imports in the future
gcm_avg_dir = wrf_dir / 'sim_avg'
try:
    gcm_avg_dir.mkdir(parents=True)
except FileExistsError:
    pass

np.savetxt(gcm_avg_dir / 'sim_avg_ppt.gz', proj_sims_ppt)
