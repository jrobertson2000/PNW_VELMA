# Trains and saves a regression model to adjust seasonal errors in VELMA+Penumbra stream temperature predictions

import __init__
import scripts.config as config
import numpy as np
import pandas as pd
from natsort import natsorted
import datetime
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import os

# =======================================================================
# Import data

# Final calibration simulation to train regression model on
calibrated_sim = 'ellsworth_baseline_03_07_21'
input_dir = config.velma_data
results_dir = config.data_path.parents[0] / 'results' / 'calibration' / calibrated_sim

# Years to compute Nash-Sutcliffe
nse_start = pd.to_datetime('01-01-2004')
nse_end = pd.to_datetime('12-31-2007')

# Years of climate driver data
forcing_start = pd.to_datetime('01-01-2003')
forcing_end = pd.to_datetime('12-31-2019')

# Stream temperature observations
streamtemp_path = config.data_path / 'hydrology' / 'ellsworth' / 'wa_ecy_gauge' / 'stream_temp' / 'ells_streamtemp_2003_2008.csv'
streamtemp_obs = pd.read_csv(streamtemp_path, usecols=['date', 'water_temp'], parse_dates=True, index_col=0)
streamtemp_obs['doy'], streamtemp_obs['year'] = streamtemp_obs.index.dayofyear, streamtemp_obs.index.year
streamtemp_obs = streamtemp_obs[(streamtemp_obs.index >= nse_start) & (streamtemp_obs.index <= nse_end)]

# Stream temperature quality codes
streamtemp_path = config.data_path / 'hydrology' / 'ellsworth' / 'wa_ecy_gauge' / 'stream_temp' / 'ells_streamtemp_2003_2008.csv'
stream_temp_quality = pd.read_csv(streamtemp_path, usecols=['date', 'quality'], parse_dates=True, index_col=0)
stream_temp_quality['doy'], stream_temp_quality[
    'year'] = stream_temp_quality.index.dayofyear, stream_temp_quality.index.year
stream_temp_quality = stream_temp_quality[(stream_temp_quality.index >= nse_start) & (stream_temp_quality.index <= nse_end)]

# Air temperature
temp_path = input_dir / 'temp' / 'ellsworth_temp_2003_2019.csv'
temp = pd.read_csv(temp_path, names=['temp'])
temp.index = pd.date_range(forcing_start, forcing_end)
temp['doy'], temp['year'] = temp.index.dayofyear, temp.index.year
temp = temp[(temp.index >= nse_start) & (temp.index <= nse_end)]

# Get stream temperature from cell writer files
cell_paths = []
for file in os.listdir(results_dir):
    if file.startswith('Cell_'):
        cell_paths.append(file)

nodes = []
for path in cell_paths:
    nodes.append(path.split('_')[-1])

cell_paths_sorted = [x for _, x in natsorted(zip(nodes, cell_paths))]

cell_results = []
for path in [cell_paths_sorted[0]]:  # Only using first cell, at Ellsworth mouth
    cell_result = pd.read_csv(results_dir / path)
    jday_pad = cell_result['Jday'].apply(lambda x: str(x).zfill(3))
    str_year = cell_result['Year'].apply(lambda x: str(x))
    cell_result['date'] = str_year + jday_pad
    rng = pd.to_datetime(cell_result['date'], format='%Y%j')
    cell_result.index = rng
    cell_result = cell_result[(cell_result.index >= nse_start) & (cell_result.index <= nse_end)]
    cell_results.append(cell_result)

# Convert to pivot tables
cell_pivots = []
for df in cell_results:
    piv = pd.pivot_table(df, index=['Jday'], columns=['Year'],
                         values='Water_Surface_Temperature(degrees_C)', dropna=False)
    cell_pivots.append(piv)

streamtemp_obs_yearly = pd.pivot_table(streamtemp_obs, index=['doy'], columns=['year'],
                                   values='water_temp', dropna=False)

streamtemp_sim_yearly = cell_pivots[0]

# =======================================================================
# Training a model to correct simulated stream temp, which overpredicts temp in winter and underpredicts in summer

streamtemps = pd.concat([streamtemp_obs.loc[:, 'water_temp'],
                         cell_results[0].loc[:, 'Water_Surface_Temperature(degrees_C)']], axis=1).dropna()

# Convert day of year to signal
day = 24 * 60 * 60
year = 365.2425 * day
df = streamtemps.copy()
timestamp_secs = pd.to_datetime(df.index)
timestamp_secs = timestamp_secs.map(datetime.datetime.timestamp)
df['year_cos'] = np.cos(timestamp_secs * (2 * np.pi / year))
df['year_sin'] = np.sin(timestamp_secs * (2 * np.pi / year))
# df['air temp'] = temp['temp']
df['air_temp_3day_avg'] = temp['temp'].rolling(3, min_periods=0).mean()
# Removing 3-day air temp as a feature yields tighter confidence bounds, but smaller R-squared

X = df.copy()
y = X.pop('water_temp')
X = sm.add_constant(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
X_train = sm.add_constant(X_train)
olsmodel = sm.OLS(y_train, X_train).fit()
print(olsmodel.summary())

# Save model
# olsmodel.save(config.data_path.parents[0] / 'models' / 'stream_temp_correction_ols.pickle')

# =======================================================================
# Test metrics
y_pred = olsmodel.predict(X_test)
streamtemps = pd.concat([streamtemp_obs.loc[:, 'water_temp'],
                         cell_results[0].loc[:, 'Water_Surface_Temperature(degrees_C)']], axis=1).dropna()

old_rmse = np.sqrt(mean_squared_error(streamtemps.iloc[:, 0], streamtemps.iloc[:, 1]))
new_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print('RMSE: {} --> {}'.format(np.round(old_rmse, 2), np.round(new_rmse, 2)))

old_mae = mean_absolute_error(streamtemps.iloc[:, 0], streamtemps.iloc[:, 1])
new_mae = mean_absolute_error(y_test, y_pred)
print('MAE: {} --> {}'.format(np.round(old_mae, 2), np.round(new_mae, 2)))

old_r2 = r2_score(streamtemps.iloc[:, 0], streamtemps.iloc[:, 1])
new_r2 = r2_score(y_test, y_pred)
print('R-squared: {} --> {}'.format(np.round(old_r2, 2), np.round(new_r2, 2)))


# =======================================================================
# Predict on new values
y_corrected_sm = olsmodel.predict(X)

cols = X.columns.tolist()
cols.insert(0, 'water_temp_corrected')
streamtemp_sim_corrected = pd.DataFrame(np.column_stack([y_corrected_sm, X]), columns=cols, index=streamtemps.index)
corrected_piv_sm = pd.pivot_table(streamtemp_sim_corrected, index=streamtemp_sim_corrected.index.dayofyear,
                                  columns=streamtemp_sim_corrected.index.year,
                                  values='water_temp_corrected', dropna=False)


# Calculate confidence intervals
ci_values95 = olsmodel.conf_int(alpha=0.05, cols=None)
ci_lower95 = (X * ci_values95.iloc[:, 0].tolist()).sum(axis=1)
ci_lower95.name = 'ci_lower95'
ci_upper95 = (X * ci_values95.iloc[:, 1].tolist()).sum(axis=1)
ci_upper95.name = 'ci_upper95'

ci_values99 = olsmodel.conf_int(alpha=0.01, cols=None)
ci_lower99 = (X * ci_values99.iloc[:, 0].tolist()).sum(axis=1)
ci_lower99.name = 'ci_lower99'
ci_upper99 = (X * ci_values99.iloc[:, 1].tolist()).sum(axis=1)
ci_upper99.name = 'ci_upper99'

data_ci = pd.concat([X, y, ci_lower95, ci_upper95, ci_lower99, ci_upper99, streamtemp_sim_corrected.loc[:, 'water_temp_corrected']],
                    axis=1)

ci_lower_yearly95 = pd.pivot_table(data_ci, index=data_ci.index.dayofyear, columns=data_ci.index.year,
                         values='ci_lower95', dropna=False)
ci_upper_yearly95 = pd.pivot_table(data_ci, index=data_ci.index.dayofyear, columns=data_ci.index.year,
                         values='ci_upper95', dropna=False)
ci_lower_yearly99 = pd.pivot_table(data_ci, index=data_ci.index.dayofyear, columns=data_ci.index.year,
                         values='ci_lower99', dropna=False)
ci_upper_yearly99 = pd.pivot_table(data_ci, index=data_ci.index.dayofyear, columns=data_ci.index.year,
                         values='ci_upper99', dropna=False)


# =======================================================================
# Observed vs. simulated (corrected) stream temp for gauge, with CI
years = streamtemp_obs_yearly.columns.get_level_values(0)
fig, axes = plt.subplots(ncols=1, nrows=len(years), figsize=(6, 9))
for col, year in enumerate(years):
    streamtemp_obs_yearly.iloc[:, col].plot(ax=axes[col], label='Observed', color='tab:blue', linewidth=1)
    corrected_piv_sm.iloc[:, col].plot(ax=axes[col], label='Simulated corrected', color='orangered', linewidth=1)
    axes[col].fill_between(ci_lower_yearly95.index,
                           ci_lower_yearly95.iloc[:, col],
                           ci_upper_yearly95.iloc[:, col], color='tab:orange', alpha=0.6, label='0.95 CI', edgecolor=None)
    axes[col].fill_between(ci_lower_yearly99.index,
                           ci_lower_yearly99.iloc[:, col],
                           ci_upper_yearly99.iloc[:, col], color='tab:orange', alpha=0.4, label='0.99 CI', edgecolor=None)
    axes[col].set_title(year)
    axes[col].set_ylim([0, 20])
axes[0].legend(loc='upper left', bbox_to_anchor=(0, 1.3), fancybox=True, ncol=4)
axes[0].set_ylabel('Stream Temperature (C)')
plt.suptitle('Corrected stream temperature with 95% confidence intervals \n (predictors=VELMA stream temp, day of year, air temp 3day avg)')
plt.tight_layout(rect=[0, 0, 1, 0.99])

