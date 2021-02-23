# Combines NLCD and stand cover layers
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy import ndimage
from soil_merger import readHeader
import importlib

importlib.reload(config)
# ======================================================================================================================

# =======================================================================
# Combine stand raster with NLCD
# =======================================================================
nlcd_path = str(config.nlcd_velma)
stands_path = str(config.cover_type_velma)
cover_key = pd.read_csv(str(config.cover_type_velma.parents[0] / 'cover_type_key.csv'))

nlcd = np.loadtxt(nlcd_path, skiprows=6)
stands = np.loadtxt(stands_path, skiprows=6)
outfile = config.cover_type_nlcd_merge_velma

nlcd = nlcd + 100

# NLCD class values
open_water = 111
dev_openspace = 121
dev_low = 122
dev_med = 123
dev_high = 124
barren = 131
forest_decid = 141
forest_evergreen = 142
forest_mixed = 143
shrub = 152
herby = 171
woody_wet = 190
emerg_herb_wet = 195

# Stand class values
bare_id = cover_key.loc[cover_key['type'] == 'BARE', 'id'].iloc[0]
bpa_id = cover_key.loc[cover_key['type'] == 'BPA', 'id'].iloc[0]
nf_id = cover_key.loc[cover_key['type'] == 'NF', 'id'].iloc[0]
conifer_id = cover_key.loc[cover_key['type'] == 'conifer', 'id'].iloc[0]

# Replace forest values of NLCD with stand types
forest = (nlcd == forest_decid) + (nlcd == forest_evergreen) + (nlcd == forest_mixed)
nlcd[forest] = stands[forest]

# Convert BARE, BPA, and NF to conifer just to get VELMA to run. Later, NF, BPA, and BARE should be low intensity developed (22)
# Value replacement mapping
# All veg is conifer, wetlands by creek mouth are open space
nlcd[(nlcd == bare_id)] = conifer_id
nlcd[(nlcd == bpa_id)] = conifer_id
nlcd[(nlcd == nf_id)] = conifer_id
nlcd[(nlcd == herby)] = conifer_id
nlcd[(nlcd == shrub)] = conifer_id
nlcd[(nlcd == woody_wet)] = dev_openspace
nlcd[(nlcd == emerg_herb_wet)] = dev_openspace
nlcd[(nlcd == dev_med)] = dev_openspace
nlcd[(nlcd == dev_high)] = dev_openspace
nlcd[(nlcd == barren)] = dev_openspace

# Erode roads by 1 pixel - they look to be about 10-20m, not 30m
road_mask = (nlcd == dev_openspace) + (nlcd == dev_low)
roads = ndimage.binary_erosion(road_mask, iterations=1)

# Replace road pixels with nearest neighbor
x, y = np.mgrid[0:nlcd.shape[0], 0:nlcd.shape[1]]
xygood = np.array((x[~road_mask], y[~road_mask])).T
xybad = np.array((x[road_mask], y[road_mask])).T
nlcd_eroded = nlcd.copy()
nlcd_eroded[road_mask] = nlcd_eroded[~road_mask][KDTree(xygood).query(xybad)[1]]

# Overlay new eroded roads
nlcd_eroded[roads] = dev_openspace

header = readHeader(stands_path)
f = open(outfile, "w")
f.write(header)
np.savetxt(f, nlcd_eroded, fmt="%i")
f.close()

# Merge key files
nlcd_key = pd.read_csv(config.nlcd_out.parents[0] / 'nlcd_classes.csv')
nlcd_key = nlcd_key.drop(['Red', 'Green', 'Blue'], axis=1)
nlcd_key = nlcd_key.rename(columns={'Value': 'id', 'NLCD_Land': 'type'})
nlcd_key['id'] = nlcd_key['id'] + 100
nlcd_key = nlcd_key[nlcd_key['id'].isin(np.unique(nlcd_eroded))]

cover_type_key = pd.read_csv(config.cover_type_velma.parents[0] / 'cover_type_key.csv')

out_key = pd.concat([cover_type_key, nlcd_key], sort=True)
out_key.to_csv(config.cover_type_velma.parents[0] / 'cover_type_merge_key.csv', index=False)

