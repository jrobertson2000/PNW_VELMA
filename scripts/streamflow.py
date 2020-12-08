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
importlib.reload(config)
# ======================================================================================================================

temp_dir = tempfile.mkdtemp()

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

# Plot
daily_flow['year'] = daily_flow.index.year
daily_flow['doy'] = daily_flow.index.dayofyear
flow_piv = pd.pivot_table(daily_flow, index=['doy'], columns=['year'], values=['flow_mm_day'])
flow_piv.plot(subplots=True)

# Add quality scores
daily_quality = df.merge(quality, left_index=True, right_index=True, how='left')
daily_quality['year'] = daily_quality.index.year
daily_quality['doy'] = daily_quality.index.dayofyear
quality_piv = pd.pivot_table(daily_quality, index=['doy'], columns=['year'], values=['Quality'])
quality_piv.plot()

# Highlight unreliable values based on quality column
# ax = flow_piv.plot(subplots=True)


# =======================================================================
# Imputing missing data
# =======================================================================
# Remove beginning and end of dataset with no monitoring data
data_start = format(flow.index.to_frame()['Date'].min(), '%Y-%m-%d')
data_end = format(flow.index.to_frame()['Date'].max(), '%Y-%m-%d')

daily_flow_imp = daily_flow[daily_flow.index >= data_start].copy()
daily_flow_imp = daily_flow_imp[daily_flow_imp.index <= data_end].copy()

daily_flow_imp['flow_imp'] = daily_flow_imp['flow_mm_day'].interpolate(method='time')
# daily_flow_imp['imp_slinear'] = daily_flow_imp['flow_mm_day'].interpolate(method='slinear')
# daily_flow_imp['imp_poly5'] = daily_flow_imp['flow_mm_day'].interpolate(method='polynomial', order=5)
# daily_flow_imp['imp_spline3'] = daily_flow_imp['flow_mm_day'].interpolate(method='spline', order=3)
# daily_flow_imp['imp_cubic'] = daily_flow_imp['flow_mm_day'].interpolate(method='cubic')

daily_flow_imp.plot(y='flow_imp')
daily_flow_imp.plot(y=['flow_imp', 'flow_mm_day'])

# Export
outfile = config.velma_data / 'runoff' / flow_path.name
daily_flow_imp['flow_imp'].to_csv(outfile, index=False, header=False)

# =======================================================================
# Imputing missing data through modeling
# For Ellsworth, only going to model Oct-Dec of 2008,
# modeling Jan-June of 2003 seems unreliable
# =======================================================================
# Feature engineering
precip = pd.read_csv(str(config.daily_ppt), parse_dates=True, index_col=0)
temp_mean = pd.read_csv(str(config.daily_temp_mean), parse_dates=True, index_col=0)
temp_mean_min = pd.read_csv(str(config.daily_temp_min), parse_dates=True, index_col=0)
temp_mean_max = pd.read_csv(str(config.daily_temp_max), parse_dates=True, index_col=0)
# vap_pres_min = pd.read_csv(str(config.vap_press_min), parse_dates=True, index_col=0)
# vap_pres_max = pd.read_csv(str(config.vap_press_max), parse_dates=True, index_col=0)
# dewpoint_temp = pd.read_csv(str(config.dewpoint_temp), parse_dates=True, index_col=0)
df = pd.concat([precip, temp_mean, temp_mean_min, temp_mean_max], axis=1)
# df = pd.concat([precip, temp_mean, temp_mean_min, temp_mean_max, vap_pres_min, vap_pres_max, dewpoint_temp], axis=1)

# Convert day of year to signal
day = 24*60*60
year = 365.2425 * day
timestamp_secs = pd.to_datetime(df.index)
timestamp_secs = timestamp_secs.map(datetime.datetime.timestamp)
df['year_cos'] = np.cos(timestamp_secs * (2 * np.pi / year))
df['year_sin'] = np.sin(timestamp_secs * (2 * np.pi / year))
# plt.plot(np.array(df['year_sin']))
# plt.plot(np.array(df['year_cos']))
# Sum of last 2 days precip
df['precip_sum-2t'] = precip.rolling(2).sum()

# Previous days' precip
df['precip_t-1'] = precip['mean_ppt_mm'].shift(1)
df['precip_t-2'] = precip['mean_ppt_mm'].shift(2)
df['precip_t-3'] = precip['mean_ppt_mm'].shift(3)

obs = df.merge(daily_flow_imp['flow_imp'], left_index=True, right_index=True, how='right')

# ========================================================


def plot_test_results(y_test, y_pred):
    results = pd.DataFrame(data=np.column_stack([y_test, y_pred]), index=y_test.index, columns=['y_test', 'y_pred'])
    results = (results * train_std['flow_imp']) + train_mean['flow_imp']
    plt.plot(results)
    plt.legend(results.columns)


# Split the data 70-20-10
n = obs.shape[0]
# obs = obs.sample(frac=1)
train_df = obs[0:int(n*0.7)]
test_df = obs[int(n*0.7):]
num_features = obs.shape[1]

cols = obs.columns.tolist()
target = cols.index('flow_imp')

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
# Predicting missing months of 2008
from datetime import timedelta
gap_start = pd.to_datetime(data_end) + timedelta(days=1)
gap_end = pd.to_datetime(end)

X_gap = df[(df.index >= gap_start) & (df.index <= gap_end)]
X_gap = (X_gap - train_mean[:-1]) / train_std[:-1]

gap_pred = svr.predict(X_gap)
gap_pred = (gap_pred * train_std['flow_imp']) + train_mean['flow_imp']

preds = pd.DataFrame(data=gap_pred, index=pd.date_range(gap_start, gap_end), columns=['flow_pred'])

# Plot estimated streamflow
plt.plot(obs['flow_imp'], label='Observed')
plt.plot(preds['flow_pred'], label='Modeled')
plt.legend()


data_begin = pd.to_datetime('01-01-2004')
df_all = df[(df.index >= data_begin) & (df.index <= gap_end)]
df_all.plot(subplots=True)
# ========================================================
# Export runoff


# ========================================================
# Alternatively, just export the full years (non-modeled) with imputed streamflow
runoff_velma = obs['flow_imp']
outfile = str(config.velma_data / 'runoff' / 'ellsworth_Q_2004_2007.csv')
runoff_velma.to_csv(outfile, header=False, index=False)

precip_velma = obs['mean_ppt_mm']
outfile = str(config.velma_data / 'precip' / 'ellsworth_ppt_2004_2019.csv')
precip_velma.to_csv(outfile, header=False, index=False)

temp_velma = obs['mean_temp_c']
outfile = str(config.velma_data / 'temp' / 'ellsworth_temp_2004_2019.csv')
temp_velma.to_csv(outfile, header=False, index=False)
