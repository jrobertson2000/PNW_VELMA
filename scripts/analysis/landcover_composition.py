# Calculate % composition of landcover classes in delineated watershed

import config as config
import numpy as np
import pandas as pd
from scipy import ndimage
import matplotlib.pyplot as plt
import importlib

importlib.reload(config)

# ======================================================================================================================
# Imports

# Ellsworth watershed outlet is at x=284, y=236. Delineated DEM exported from JPDEM after flat-processing
del_dem = np.loadtxt(config.dem_velma.parents[0] / 'delineated_dem.asc', skiprows=6)
watershed = (del_dem != -9999)
plt.imshow(watershed)

# ================================
# Stands
stands_path = str(config.cover_type_velma)
cover_key = pd.read_csv(str(config.cover_type_velma.parents[0] / 'cover_type_key.csv'))
stands = np.loadtxt(stands_path, skiprows=6)

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

# =======================================================================
# Combine covers

# Erode NLCD roads by 1 pixel - they look to be about 10-20m, not 30m
road_mask = (nlcd == nlcd_dev_openspace) + (nlcd == nlcd_dev_low)
roads = ndimage.binary_erosion(road_mask, iterations=1)

# Place erodedNLCD roads on top of CCAP
ccap[roads] = ccap_dirt

# Add NLCD deciduous forest to CCAP
ccap[nlcd_forest_decid] = nlcd_forest_decid

# =======================================================================
# Calculate composition

# Mask out values outside delineated watershed
cover_mask = ccap.copy()
cover_mask[~watershed] = np.nan

# Count class occurrences within
cover_mask_flat = cover_mask[~np.isnan(cover_mask)].flatten()
cover_count = np.bincount(cover_mask_flat.astype('int'))
cover_count = cover_count[cover_count != 0]
stack = np.column_stack([np.unique(cover_mask_flat), cover_count])
counts = pd.DataFrame(data=stack, columns=['Class', 'Count'])
counts['Count'] = counts['Count'] / cover_mask_flat.shape[0]


