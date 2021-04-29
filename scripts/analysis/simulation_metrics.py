# Combine the results of all calibration simulations in the results directory into one neat CSV
# Can be copy-pasted into .xlsx template for easy viewing and highlighting
# Script written in Python 3.7

import numpy as np
import pandas as pd
import os
from natsort import natsorted
import config
import itertools
from sklearn.metrics import mean_squared_error, r2_score
import xml.etree.ElementTree as ET
# =======================================================================
# Config
results_dir = config.velma_data.parents[1] / 'results' / 'calibration' / 'corrected_harvest'
xml_dir = config.velma_data.parents[1] / 'xml' / 'calibration' / 'corrected_harvest'

sims = natsorted(next(os.walk(results_dir))[1])
# removed = ['ellsworth_baseline_03_07', 'ellsworth_baseline_03_07_2']
removed = ['penumbra_test', 'subzero_water_balance']
sims = [x for x in sims if x not in removed]

results_dfs = []
params_dfs = []

# Years for which Nash-Sutcliffe is calculated
years = [2004, 2005, 2006, 2007]

# Import observed runoff
runoff_path = config.velma_data / 'runoff' / 'ellsworth_Q_2003_2007_dummy.csv'
runoff_start = pd.to_datetime('01-01-2003')
runoff_end = pd.to_datetime('12-31-2007')
nse_start = pd.to_datetime('01-01-{}'.format(min(years)))
nse_end = pd.to_datetime('12-31-{}'.format(max(years)))
runoff_obs = pd.read_csv(runoff_path, names=['runoff_obs'])
runoff_obs.index = pd.date_range(runoff_start, runoff_end)
runoff_obs['doy'], runoff_obs['year'] = runoff_obs.index.dayofyear, runoff_obs.index.year
runoff_obs = runoff_obs[(runoff_obs.index >= nse_start) & (runoff_obs.index <= nse_end)]

# Runoff quality codes
flow_path = config.data_path / 'hydrology' / 'ellsworth' / 'wa_ecy_gauge' / 'streamflow' / 'ells_streamflow_2003_2008.csv'
quality = pd.read_csv(flow_path, usecols=['Date', 'Quality'], parse_dates=True, index_col=0)
quality = quality[(quality.index >= nse_start) & (quality.index <= nse_end)]


def r2_rmse_groupby(g):
    r2 = r2_score(g['runoff_obs'], g['Runoff_All(mm/day)_Delineated_Average'])
    rmse = np.sqrt(mean_squared_error(g['runoff_obs'], g['Runoff_All(mm/day)_Delineated_Average']))
    return pd.Series(dict(r2=r2, rmse=rmse))


def NS(s, o):
    """
        Nash Sutcliffe efficiency coefficient
        input:
        s: simulated
        o: observed
        output:
        ns: Nash Sutcliffe efficient coefficient
        """
    # s,o = filter_nan(s,o)
    return 1 - np.sum((s-o)**2)/np.sum((o-np.mean(o))**2)


def remove_unreliable_runoff(runoff_s, runoff_o, runoff_quality_codes, years):
    edited_nses = []
    df = pd.concat([runoff_s, runoff_o, runoff_quality_codes], axis=1)
    df_edited = df.drop(df[(df['Quality'] == 160) | (df['Quality'] == 161) | (df['Quality'] == 179) | (df['Quality'] == 254)].index)
    sim_yearly = pd.pivot_table(df_edited[['Runoff_All(mm/day)_Delineated_Average', 'doy', 'year']],
                                index=['doy'],
                                columns=['year'],
                                values=['Runoff_All(mm/day)_Delineated_Average'])

    obs_yearly = pd.pivot_table(df_edited[['runoff_obs', 'doy', 'year']],
                                index=['doy'],
                                columns=['year'],
                                values=['runoff_obs'])

    for i, j in zip(list(range(len(years))), years):
        edited = NS(sim_yearly.iloc[:, i], obs_yearly.iloc[:, i])
        edited_nses.append(edited)

    df_edited_04_07 = df_edited[(df_edited.index >= pd.to_datetime('2004-01-01'))]
    edited_tot = NS(df_edited_04_07['Runoff_All(mm/day)_Delineated_Average'], df_edited_04_07['runoff_obs'])
    edited_nses.insert(0, edited_tot)
    return edited_nses


def parseXML(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for item in root.findall('soil/siltloam/setSoilLayerWeights'):
        return item.text


for sim in sims:
    print(sim)
    sim_dir = results_dir / sim
    files = os.listdir(sim_dir)
    if 'AnnualHydrologyResults.csv' not in files:
        continue

    # Calculate R2 and RMSE
    daily_results = pd.read_csv(sim_dir / 'DailyResults.csv')
    jday_pad = daily_results['Day'].apply(lambda x: str(x).zfill(3))
    str_year = daily_results['Year'].apply(lambda x: str(x))
    daily_results['year_jday'] = str_year + jday_pad
    daily_results.index = pd.to_datetime(daily_results['year_jday'], format='%Y%j')
    daily_results = daily_results[(daily_results.index >= nse_start) & (daily_results.index <= nse_end)]

    runoff = pd.concat([daily_results[['Year', 'Runoff_All(mm/day)_Delineated_Average']], runoff_obs], axis=1)
    r2_rmse = runoff.groupby('Year').apply(r2_rmse_groupby)
    rmses = r2_rmse.iloc[-len(years):, 1]

    # Get NSE from coefficients file - oddly, can't reproduce using an average or NSE equation
    nse_file = pd.read_csv(sim_dir / 'NashSutcliffeCoefficients.txt', header=None)
    NSE_tot = [float(nse_file.iloc[0].values[0].split('=')[1].split(' ')[0])]
    rmse_tot = [float(nse_file.iloc[1].values[0].split('=')[1].split(' ')[0])]

    # Get results
    hydro_results = pd.read_csv(sim_dir / 'AnnualHydrologyResults.csv')
    PET_ratio = hydro_results['Total_(AET/PET)'].iloc[-len(years):]
    AET = hydro_results['Total_AET(mm)'].iloc[-len(years):]
    AET_rainmelt = hydro_results['Total_(AET/(Rain+Melt))'].iloc[-len(years):]
    NSE = hydro_results['Runoff_Nash-Sutcliffe_Coefficient'].iloc[-len(years):]
    sim_obs = hydro_results['Total_Fraction(sim/obs)'].iloc[-len(years):]

    # NSE with unreliable runoff values removed
    NSE_reliable = remove_unreliable_runoff(runoff['Runoff_All(mm/day)_Delineated_Average'], runoff_obs, quality, years)

    metric_stack = np.concatenate([NSE_tot, NSE, NSE_reliable, rmse_tot, rmses, PET_ratio,
                                   AET, AET_rainmelt, sim_obs], axis=0)

    row_index = [['NSE_tot'],
                 ['NSE {}'.format(year) for year in years],
                 ['NSE_reliable_tot'],
                 ['NSE_reliable {}'.format(year) for year in years],
                 ['RMSE_tot'],
                 ['RMSE {}'.format(year) for year in years],
                 ['AET/PET {}'.format(year) for year in years],
                 ['AET {}'.format(year) for year in years],
                 ['AET/rain+melt {}'.format(year) for year in years],
                 ['sim/obs {}'.format(year) for year in years]]
    row_index = list(itertools.chain(*row_index))
    results_df = pd.DataFrame(data=metric_stack, columns=[sim], index=row_index)
    results_dfs.append(results_df)

    # Get configuration parameters
    config_params = pd.read_csv(sim_dir / 'SimulationConfiguration.csv', names=['param', 'value'])

    param_names = ['be', 'Ks_siltyclayloam', 'ksl_siltyclayloam', 'ksv_siltyclayloam',
                   'Ks_siltloam', 'ksl_siltloam', 'ksv_siltloam', 'soil_depth']

    param_keys = ['/calibration/VelmaCalibration.properties/be', '/soil/siltyclayloam/surfaceKs',
                  '/soil/siltyclayloam/ksLateralExponentialDecayFactor',
                  '/soil/siltyclayloam/ksVerticalExponentialDecayFactor',
                  '/soil/siltloam/surfaceKs', '/soil/siltloam/ksLateralExponentialDecayFactor',
                  '/soil/siltloam/ksVerticalExponentialDecayFactor', '/soil/siltyclayloam/soilColumnDepth']

    param_values = []
    for key in param_keys:
        param_values.append(config_params[config_params['param'] == key]['value'].item())

    # Get soil layer weights
    xml_path = xml_dir / '{}.xml'.format(sim)
    soil_weights = parseXML(xml_path)

    param_names.append('soil_layer_weights')
    param_values.append(soil_weights)

    params_df = pd.DataFrame(data=param_values, columns=[sim], index=param_names)
    params_dfs.append(params_df)

params = pd.concat(params_dfs, axis=1)
results = pd.concat(results_dfs, axis=1)
output = pd.concat([results, params], axis=0)
output.to_csv(results_dir.parents[0] / 'simulation_metrics.csv')

