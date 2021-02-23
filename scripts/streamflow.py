# Visualize streamflow time series and fill missing data
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import tempfile
import datetime
from sklearn.svm import SVR
import geopandas as gpd
from sklearn.metrics import mean_squared_error as mse
import matplotlib.pyplot as plt
import importlib

# ======================================================================================================================

tmp_dir = tempfile.mkdtemp()

# =======================================================================
# Visualizing streamflow
# =======================================================================

flow_path = config.streamflow
# flow = pd.read_csv(str(flow_path))
# flow = pd.read_csv(str(flow_path), header=0, squeeze=True)
flow = pd.read_csv(str(flow_path), usecols=['Date', 'Flow_cfs'], parse_dates=True, index_col=0)
quality = pd.read_csv(str(flow_path), usecols=['Date', 'Quality'], parse_dates=True, index_col=0)

# Convert streamflow from cfs to mm/day
# 2.446576 ft3/sec =  1m3/35.314667ft3 * 1/km2 * 86400sec/1day * 1km2/1000000m2 * 1000mm/1m
ft3_sec = (1/35.314667) * 86400 * (1/1000000) * 1000
area = 13.7393  # area of upstream Ellsworth watershed, sq. km
flow['flow_mm_day'] = (flow['Flow_cfs'] / area) * ft3_sec
flow.drop('Flow_cfs', axis=1, inplace=True)

# Expand date range to include every day of all the years present
begin = '01-01-{}'.format(flow.index.to_frame()['Date'].min().year)
end = '12-31-{}'.format(flow.index.to_frame()['Date'].max().year)
rng = pd.date_range(begin, end)
df = pd.DataFrame(index=rng)
daily_flow = df.merge(flow, left_index=True, right_index=True, how='left')

# Plot available runoff
daily_flow['year'] = daily_flow.index.year
daily_flow['doy'] = daily_flow.index.dayofyear
flow_piv = pd.pivot_table(daily_flow, index=['doy'], columns=['year'], values=['flow_mm_day'])
flow_piv.plot(subplots=True, legend=False)
plt.ylabel('Flow (mm/day)')
plt.xlabel('Day of Year')

# =======================================================================
# Imputing missing data through modeling:
# Ellsworth is missing Jan-Jun of 2003 and Oct-Dec of 2008. Will just remove those years
# Also missing small gaps from 2004-2007
# =======================================================================
# Import data and feature engineering
temp_mean = pd.read_csv(str(config.daily_temp_mean), parse_dates=True, index_col=0)
temp_mean_min = pd.read_csv(str(config.daily_temp_min), parse_dates=True, index_col=0)
temp_mean_max = pd.read_csv(str(config.daily_temp_max), parse_dates=True, index_col=0)

# Using average of PRISM precip and a nearby Naselle rain gauge
precip_prism = pd.read_csv(str(config.daily_ppt), parse_dates=True, index_col=0)
gauge_data = pd.read_csv(config.daily_ppt.parents[0] / 'GHCND_USC00455774_1929_2020.csv', parse_dates=True, index_col=5)
gauge_data['SNOW'].fillna(0, inplace=True)
gauge_data['SNOW_SWE'] = gauge_data['SNOW'] / 13
gauge_data['PRCP_TOT'] = gauge_data['PRCP'] + gauge_data['SNOW_SWE']
precip_gauge = gauge_data[['PRCP_TOT']].copy()
precip_gauge['PRCP_TOT'] = precip_gauge['PRCP_TOT'].combine_first(precip_prism['mean_ppt_mm'])

prism_start = precip_prism.index.min()
prism_end = precip_prism.index.max()
precip_gauge = precip_gauge[(precip_gauge.index >= prism_start) & (precip_gauge.index <= prism_end)].copy()

precip = precip_prism.merge(precip_gauge, left_index=True, right_index=True, how='left')
precip_mean = pd.DataFrame(precip.mean(axis=1), columns=['ppt'])
df = pd.concat([precip_mean, temp_mean, temp_mean_min, temp_mean_max], axis=1)

# Convert day of year to signal
day = 24*60*60
year = 365.2425 * day
timestamp_secs = pd.to_datetime(df.index)
timestamp_secs = timestamp_secs.map(datetime.datetime.timestamp)
df['year_cos'] = np.cos(timestamp_secs * (2 * np.pi / year))
df['year_sin'] = np.sin(timestamp_secs * (2 * np.pi / year))

# Sum of last 2 days precip
df['precip_sum-2t'] = precip_mean.rolling(2).sum()

# Previous days' precip
df['precip_t-1'] = precip_mean['ppt'].shift(1)
df['precip_t-2'] = precip_mean['ppt'].shift(2)
df['precip_t-3'] = precip_mean['ppt'].shift(3)

obs = df.merge(daily_flow['flow_mm_day'], left_index=True, right_index=True, how='right')

# Set aside dates with missing flow measurements
gap_data = obs[obs['flow_mm_day'].isna()]
obs.dropna(inplace=True)
# ========================================================


def plot_test_results(y_test, y_pred):
    results = pd.DataFrame(data=np.column_stack([y_test, y_pred]), index=y_test.index, columns=['y_test', 'y_pred'])
    results = (results * train_std['flow_mm_day']) + train_mean['flow_mm_day']
    plt.plot(results)
    plt.legend(results.columns)


# Split the data 70-20-10
n = obs.shape[0]
train_df = obs[0:int(n*0.7)]
test_df = obs[int(n*0.7):]
num_features = obs.shape[1]

cols = obs.columns.tolist()
target = cols.index('flow_mm_day')

# Normalize
train_mean = train_df.mean()
train_std = train_df.std()

train_df = (train_df - train_mean) / train_std
test_df = (test_df - train_mean) / train_std

X_train, y_train = train_df.iloc[:, 0:target], train_df.iloc[:, target]
X_test, y_test = test_df.iloc[:, 0:target], test_df.iloc[:, target]

svr = SVR(kernel='rbf', C=1, gamma='auto', epsilon=0.1)
svr.fit(X_train, y_train)

y_pred = svr.predict(X_test)
print(mse(y_test, y_pred))

plot_test_results(y_test, y_pred)

# ========================================================
# Predicting small data gaps from 2004-2007

velma_start = pd.to_datetime('01-01-2004')
velma_end = pd.to_datetime('12-31-2007')
gap_data_04_07 = gap_data[(gap_data.index >= velma_start) & (gap_data.index <= velma_end)].copy()

X_gap = gap_data_04_07.drop(columns='flow_mm_day', axis=1)
X_gap = (X_gap - train_mean[:-1]) / train_std[:-1]
gap_pred = svr.predict(X_gap)
gap_pred = (gap_pred * train_std['flow_mm_day']) + train_mean['flow_mm_day']

# Add dates to predicted flow
rng = pd.date_range(velma_start, velma_end)
date_df = pd.DataFrame(index=rng)
obs_04_07 = date_df.merge(obs, left_index=True, right_index=True, how='left')

gap_data_04_07['flow_mm_day'] = gap_pred
imp_04_07 = date_df.merge(gap_data_04_07, left_index=True, right_index=True, how='left')

# Combine the data
data_04_07 = pd.concat([obs, gap_data_04_07]).sort_index()

plt.plot(data_04_07['flow_mm_day'], label='Observed')
# plt.plot(obs_04_07['flow_mm_day'], label='Observed')
plt.plot(imp_04_07['flow_mm_day'], label='Modeled')
plt.legend()

# ========================================================
# # Export runoff and precip/temp for given time period

# Runoff
velma_start = pd.to_datetime('01-01-2004')
velma_end = pd.to_datetime('12-31-2007')
runoff_velma = data_04_07[(data_04_07.index >= velma_start) & (data_04_07.index <= velma_end)]['flow_mm_day']
outfile = str(config.velma_data / 'runoff' / 'ellsworth_Q_2004_2007.csv')
if len(pd.date_range(velma_start, velma_end)) != len(runoff_velma):
    print('STOP: Duplicates/missing values exist in output file: ', outfile)
runoff_velma.to_csv(outfile, header=False, index=False)

# Runoff starting from 2003 (using filler values)
velma_start = pd.to_datetime('01-01-2003')
velma_end = pd.to_datetime('12-31-2007')
rng = pd.date_range(velma_start, velma_end)
date_df = pd.DataFrame(index=rng)
data_03_07 = date_df.merge(data_04_07, left_index=True, right_index=True, how='left')['flow_mm_day'].fillna(0)
outfile = str(config.velma_data / 'runoff' / 'ellsworth_Q_2003_2007.csv')
if len(pd.date_range(velma_start, velma_end)) != len(data_03_07):
    print('STOP: Duplicates/missing values exist in output file: ', outfile)
data_03_07.to_csv(outfile, header=False, index=False)

# Precipitation and Temperature
velma_start = pd.to_datetime('01-01-2003')
velma_end = pd.to_datetime('12-31-2019')
precip_velma = df[(df.index >= velma_start) & (df.index <= velma_end)]['ppt']
outfile = str(config.velma_data / 'precip' / 'PRISM_gauge_avg_ppt_2003_2019.csv')
if len(pd.date_range(velma_start, velma_end)) != len(precip_velma):
    print('STOP: Duplicates/missing values exist in output file: ', outfile)
precip_velma.to_csv(outfile, header=False, index=False)

temp_velma = df[(df.index >= velma_start) & (df.index <= velma_end)]['mean_temp_c']
outfile = str(config.velma_data / 'temp' / 'ellsworth_temp_2003_2019.csv')
if len(pd.date_range(velma_start, velma_end)) != len(temp_velma):
    print('STOP: Duplicates/missing values exist in output file: ', outfile)
temp_velma.to_csv(outfile, header=False, index=False)

