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

nlcd = np.loadtxt(nlcd_path, skiprows=6)
stands = np.loadtxt(stands_path, skiprows=6)
outfile = config.cover_type_merge_velma

nlcd = nlcd + 100

# Replace forest values of NLCD with stand types
# 42 = Evergreen Forest
# 41 = Deciduous Forest
# 43 = Mixed Forest
forest = (nlcd == 141) + (nlcd == 142) + (nlcd == 143)
nlcd[forest] = stands[forest]

# Erode roads by 1 pixel - they look to be about 10-20m, not 30m
road_mask = (nlcd == 121) + (nlcd == 122)
roads = ndimage.binary_erosion(road_mask, iterations=1)

# Replace road pixels with nearest neighbor
x, y = np.mgrid[0:nlcd.shape[0], 0:nlcd.shape[1]]
xygood = np.array((x[~road_mask], y[~road_mask])).T
xybad = np.array((x[road_mask], y[road_mask])).T
nlcd_eroded = nlcd.copy()
nlcd_eroded[road_mask] = nlcd_eroded[~road_mask][KDTree(xygood).query(xybad)[1]]

# Overlay new eroded roads
nlcd_eroded[roads] = 121

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
