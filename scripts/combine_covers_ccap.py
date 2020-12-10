# Combines ccap and stand cover layers
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy import ndimage
from soil_merger import readHeader
import importlib
import matplotlib.pyplot as plt
importlib.reload(config)
# ======================================================================================================================

# =======================================================================
# Combine stand raster with ccap
# =======================================================================
# Imports

# ================================
# Stands
stands_path = str(config.cover_type_velma)
cover_key = pd.read_csv(str(config.cover_type_velma.parents[0] / 'cover_type_key.csv'))
stands = np.loadtxt(stands_path, skiprows=6)
outfile = config.cover_type_ccap_merge_velma

# ================================
# NOAA C-CAP
ccap_path = str(config.noaa_ccap_velma)
ccap = np.loadtxt(ccap_path, skiprows=6)
ccap = ccap + 100

# CCAP class values
ccap_NA = 100
ccap_herby = 101
ccap_dirt = 102
ccap_developed = 103
ccap_water = 104
ccap_forest = 105
ccap_shrub = 106

# ================================
# NLCD
nlcd_path = str(config.nlcd_velma)
stands_path = str(config.cover_type_velma)
cover_key = pd.read_csv(str(config.cover_type_velma.parents[0] / 'cover_type_key.csv'))
nlcd = np.loadtxt(nlcd_path, skiprows=6)


nlcd = nlcd + 100

# NLCD class values
nlcd_open_water = 111
nlcd_dev_openspace = 121
nlcd_dev_low = 122
nlcd_dev_med = 123
nlcd_dev_high = 124
nlcd_barren = 131
nlcd_forest_decid = 141
nlcd_forest_evergreen = 142
nlcd_forest_mixed = 143
nlcd_shrub = 152
nlcd_herby = 171
nlcd_woody_wet = 190
nlcd_emerg_herb_wet = 195

# ================================
# Impervious layer
imperv_path = str(config.imperv_velma)
imperv = np.loadtxt(imperv_path, skiprows=6)

# ================================
# Convert and merge landcover classes

# Stand class values
bare_id = cover_key.loc[cover_key['type'] == 'BARE', 'id'].iloc[0]
bpa_id = cover_key.loc[cover_key['type'] == 'BPA', 'id'].iloc[0]
nf_id = cover_key.loc[cover_key['type'] == 'NF', 'id'].iloc[0]
conifer_id = cover_key.loc[cover_key['type'] == 'conifer', 'id'].iloc[0]

# Convert CCAP developed to dirt
ccap[(ccap == ccap_developed)] = ccap_dirt

# Replace forest values of ccap with stand types
ccap[(ccap == ccap_forest)] = stands[(ccap == ccap_forest)]

# Replace bare, bpa, and nf that were in stands with CCAP dirt value
ccap[(ccap == bare_id)] = ccap_dirt
ccap[(ccap == bpa_id)] = ccap_dirt
ccap[(ccap == nf_id)] = ccap_dirt

# Overlay NLCD deciduous forests on CCAP
ccap[(nlcd == nlcd_forest_decid)] = nlcd_forest_decid

# Convert CCAP shrub and herbaceous to dirt for now
ccap[(ccap == ccap_herby)] = ccap_dirt
ccap[(ccap == ccap_shrub)] = ccap_dirt

# Erode NLCD roads by 1 pixel - they look to be about 10-20m, not 30m
road_mask = (nlcd == nlcd_dev_openspace) + (nlcd == nlcd_dev_low)
roads = ndimage.binary_erosion(road_mask, iterations=1)

# Replace developed/dirt pixels with nearest neighbor
x, y = np.mgrid[0:nlcd.shape[0], 0:nlcd.shape[1]]
xygood = np.array((x[~road_mask], y[~road_mask])).T
xybad = np.array((x[road_mask], y[road_mask])).T
ccap_eroded = ccap.copy()
ccap_eroded[road_mask] = ccap_eroded[~road_mask][KDTree(xygood).query(xybad)[1]]

# Overlay new eroded roads from NLCD onto CCAP
ccap[roads] = ccap_dirt

header = readHeader(stands_path)
f = open(outfile, "w")
f.write(header)
np.savetxt(f, ccap, fmt="%i")
f.close()

# # Merge key files
# ccap_key = pd.read_csv(config.ccap_out.parents[0] / 'ccap_classes.csv')
# ccap_key = ccap_key.drop(['Red', 'Green', 'Blue'], axis=1)
# ccap_key = ccap_key.rename(columns={'Value': 'id', 'ccap_Land': 'type'})
# ccap_key['id'] = ccap_key['id'] + 100
# ccap_key = ccap_key[ccap_key['id'].isin(np.unique(ccap_eroded))]
#
# cover_type_key = pd.read_csv(config.cover_type_velma.parents[0] / 'cover_type_key.csv')
#
# out_key = pd.concat([cover_type_key, ccap_key], sort=True)
# out_key.to_csv(config.cover_type_velma.parents[0] / 'cover_type_merge_key.csv', index=False)
#
