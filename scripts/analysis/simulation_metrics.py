# Combines the results of all simulations in the results directory into one neat CSV

import numpy as np
import pandas as pd
import os
from natsort import natsorted
import config
from sklearn.metrics import mean_squared_error, r2_score

results_dir = config.velma_data.parents[1] / 'results'
xml_dir = config.velma_data.parents[1] / 'velma' / 'xml'

sims = natsorted(next(os.walk(results_dir))[1])

results_dfs = []
params_dfs = []


def r2_rmse_groupby(g):
    r2 = r2_score(g['runoff_obs'], g['Runoff_All(mm/day)_Delineated_Average'])
    rmse = np.sqrt(mean_squared_error(g['runoff_obs'], g['Runoff_All(mm/day)_Delineated_Average']))
    return pd.Series(dict(r2=r2, rmse=rmse))


for sim in sims:
    print(sim)
    sim_dir = results_dir / sim
    files = os.listdir(sim_dir)
    if 'AnnualHydrologyResults.csv' not in files:
        continue

    # Calculate R2 and RMSE
    daily_results = pd.read_csv(sim_dir / 'DailyResults.csv')
    daily_results = daily_results[daily_results['Year'] <= 2007]
    runoff_obs = pd.read_csv(config.velma_data / 'runoff' / 'ellsworth_Q_2004_2007.csv', names=['runoff_obs'])
    runoff = pd.concat([daily_results[['Year', 'Runoff_All(mm/day)_Delineated_Average']], runoff_obs], axis=1)
    r2_05_07 = [r2_score(runoff[runoff['Year'] > 2004]['runoff_obs'],
                        runoff[runoff['Year'] > 2004]['Runoff_All(mm/day)_Delineated_Average'])]
    rmse_05_07 = [np.sqrt(mean_squared_error(runoff[runoff['Year'] > 2004]['runoff_obs'],
                        runoff[runoff['Year'] > 2004]['Runoff_All(mm/day)_Delineated_Average']))]
    r2_rmse = runoff.groupby('Year').apply(r2_rmse_groupby)
    rmses = r2_rmse.iloc[:, 1]

    # Get results
    hydro_results = pd.read_csv(sim_dir / 'AnnualHydrologyResults.csv')
    PET_ratio = hydro_results['Total_(AET/PET)']
    AET = hydro_results['Total_AET(mm)']
    AET_rainmelt = hydro_results['Total_(AET/(Rain+Melt))']
    NES = hydro_results['Runoff_Nash-Sutcliffe_Coefficient']
    NES_05_07 = [np.mean(NES[1:])]
    sim_obs = hydro_results['Total_Fraction(sim/obs)']
    metric_stack = np.concatenate([NES_05_07, NES, r2_05_07, rmse_05_07, rmses, PET_ratio, AET, AET_rainmelt, sim_obs], axis=0)
    row_index = ['NES 05-07',
                 'NES 2004', 'NES 2005', 'NES 2006', 'NES 2007',
                 'R2 05-07',
                 'RMSE 05-07',
                 'RMSE 2004', 'RMSE 2005', 'RMSE 2006', 'RMSE 2007',
                 'AET/PET 2004', 'AET/PET 2005', 'AET/PET 2006', 'AET/PET 2007',
                 'AET 2004', 'AET 2005', 'AET 2006', 'AET 2007',
                 'AET/rain+melt 2004', 'AET/rain+melt 2005', 'AET/rain+melt 2006', 'AET/rain+melt 2007',
                 'sim/obs 2004', 'sim/obs 2005', 'sim/obs 2006', 'sim/obs 2007']
    results_df = pd.DataFrame(data=metric_stack, columns=[sim], index=row_index)
    results_dfs.append(results_df)

    # Get configuration parameters
    config_params = pd.read_csv(sim_dir / 'SimulationConfiguration.csv', names=['param', 'value'])

    param_names = ['be', 'Ks_siltyclayloam', 'ksl1', 'ksv1',
                   'Ks_siltloam', 'ksl2', 'ksv2', 'soil_depth']

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


