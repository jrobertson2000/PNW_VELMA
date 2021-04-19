# Export observed runoff for given time period, with year 1 being a dummy year of 0s to allow VELMA to spin-up
# Script written in Python 3.7

import config as config
import pandas as pd
# =======================================================================
# Config

start = pd.to_datetime('01-01-2003')
end = pd.to_datetime('12-31-2007')

# Import raw flow data from Dept. of Ecology - data should be daily and in cfs
flow_path = config.streamflow
flow = pd.read_csv(flow_path, usecols=['Date', 'Flow_cfs'], parse_dates=True, index_col=0)
quality = pd.read_csv(flow_path, usecols=['Date', 'Quality'], parse_dates=True, index_col=0)

# Convert streamflow from cfs to mm/day
# 2.446576 ft3/sec =  1m3/35.314667ft3 * 1/km2 * 86400sec/1day * 1km2/1000000m2 * 1000mm/1m
ft3_sec = (1/35.314667) * 86400 * (1/1000000) * 1000
area = 13.7393  # area of upstream Ellsworth watershed, sq. km
flow['flow_mm_day'] = (flow['Flow_cfs'] / area) * ft3_sec
flow.drop('Flow_cfs', axis=1, inplace=True)

# Expand date range beyond water years to include all desired years
rng = pd.date_range(start, end)
df = pd.DataFrame(index=rng)
daily_flow = df.merge(flow, left_index=True, right_index=True, how='left')

# Fill all days in calendar year 2003 with dummy values 0s. This will allow VELMA to spin-up for a full year
# without computing Nash-Sutcliffe
daily_flow[(daily_flow.index.year == start.year)] = 0

# Export runoff from 2003-2007 (using filler values for 2003)
outfile = config.velma_data / 'runoff' / 'ellsworth_Q_2003_2007_dummy.csv'
try:
    outfile.parents[0].mkdir(parents=True)
except FileExistsError:
    pass
if len(pd.date_range(start, end)) != len(daily_flow):
    print('STOP: Duplicates/missing values exist in output file: ', outfile)
daily_flow.to_csv(outfile, header=False, index=False)
