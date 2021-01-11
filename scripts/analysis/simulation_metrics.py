# Combines the results of all simulations in the results directory into one neat CSV

import numpy as np
import pandas as pd
import os
from natsort import natsorted
import config

results_dir = config.velma_data.parents[1] / 'results'
xml_dir = config.velma_data.parents[1] / 'velma' / 'xml'

sims = natsorted(next(os.walk(results_dir))[1])

results_dfs = []
params_dfs = []

for sim in sims:
    print(sim)
    sim_dir = results_dir / sim
    files = os.listdir(sim_dir)
    if 'AnnualHydrologyResults.csv' not in files:
        continue

    # Get results
    hydro_results = pd.read_csv(sim_dir / 'AnnualHydrologyResults.csv')
    PET_ratio = hydro_results['Total_(AET/PET)']
    NES = hydro_results['Runoff_Nash-Sutcliffe_Coefficient']
    NES_05_07 = [np.mean(NES[1:])]
    sim_obs = hydro_results['Total_Fraction(sim/obs)']
    metric_stack = np.concatenate([NES_05_07, NES, PET_ratio, sim_obs])
    row_index = ['NES 05-07', 'NES 2004', 'NES 2005', 'NES 2006', 'NES 2007',
                 'AET/PET 2004', 'AET/PET 2005', 'AET/PET 2006', 'AET/PET 2007',
                 'sim/obs 2004', 'sim/obs 2005', 'sim/obs 2006', 'sim/obs 2007']
    results_df = pd.DataFrame(data=metric_stack, columns=[sim], index=row_index)
    results_dfs.append(results_df)

    # Get configuration parameters
    config_params = pd.read_csv(sim_dir / 'SimulationConfiguration.csv', names=['param', 'value'])

    param_names = ['be', 'surfaceKs1', 'ksl1', 'ksv1',
                   'surfaceKs2', 'ksl2', 'ksv2', 'soil_depth']

    param_keys = ['/calibration/VelmaCalibration.properties/be', '/soil/siltyclayloam/surfaceKs',
                  '/soil/siltyclayloam/ksLateralExponentialDecayFactor',
                  '/soil/siltyclayloam/ksVerticalExponentialDecayFactor',
                  '/soil/siltloam/surfaceKs', '/soil/siltloam/ksLateralExponentialDecayFactor',
                  '/soil/siltloam/ksVerticalExponentialDecayFactor', '/soil/siltyclayloam/soilColumnDepth']

    param_values = []
    for key in param_keys:
        param_values.append(config_params[config_params['param'] == key]['value'].item())

    params_df = pd.DataFrame(data=param_values, columns=[sim], index=param_names)
    params_dfs.append(params_df)

params = pd.concat(params_dfs, axis=1)
results = pd.concat(results_dfs, axis=1)
output = pd.concat([results, params], axis=0)
output.to_csv(results_dir / 'simulation_metrics.csv')


