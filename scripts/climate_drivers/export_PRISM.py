import __init__
import scripts.config as config
import pandas as pd
import matplotlib.pyplot as plt
import mpld3
import numpy as np

start = pd.to_datetime('01-01-1984')
end = pd.to_datetime('12-31-2020')

# Average PRISM and Naselle gauge precipitation
gauge = pd.read_csv(config.daily_ppt.parents[0] / 'GHCND_USC00455774_1929_2020.csv', parse_dates=True, index_col=5)
gauge['SNOW'].fillna(0, inplace=True)
gauge['SNOW_SWE'] = gauge['SNOW'] / 13
gauge['PRCP_TOT'] = gauge['PRCP'] + gauge['SNOW_SWE']
gauge_precip = gauge[['PRCP_TOT']]

prism_precip = pd.read_csv(str(config.daily_ppt.parents[0] / 'prism_ppt_1981_2020_daily.csv'), parse_dates=True, index_col=0)

# Expand precip record to full date range in case some days are missing
rng = pd.date_range(start, end)
date_df = pd.DataFrame(index=rng)
gauge_precip_velma = date_df.merge(gauge_precip, left_index=True, right_index=True, how='left')
prism_precip_velma = date_df.merge(prism_precip, left_index=True, right_index=True, how='left')

prism_precip_mean = pd.concat([gauge_precip_velma, prism_precip_velma], axis=1)
prism_precip_mean['avg_precip'] = prism_precip_mean.mean(axis=1)
obs_p = prism_precip_mean.loc[:, ['avg_precip']]

# Air temperature
temp_path = config.daily_temp_mean.parents[0] / 'prism_temp_1981_2020_daily.csv'
temp = pd.read_csv(temp_path, parse_dates=True, index_col=0)
obs_t = temp[(temp.index >= start) & (temp.index <= end)]

# Export gauge and PRISM averaged precip
outfile_p = str(config.velma_data / 'precip' / 'PRISM_gauge_avg_ppt_{}_{}.csv'.format(start.year, end.year))
if len(pd.date_range(start, end)) != len(obs_p):
    print('STOP: Duplicates/missing values exist in output file: ', outfile_p)
obs_p.to_csv(outfile_p, header=False, index=False)

# Export PRISM temp
outfile_t = str(config.velma_data / 'temp' / 'PRISM_temp_{}_{}.csv'.format(start.year, end.year))
if len(pd.date_range(start, end)) != len(obs_t):
    print('STOP: Duplicates/missing values exist in output file: ', outfile_t)
obs_t.to_csv(outfile_t, header=False, index=False)