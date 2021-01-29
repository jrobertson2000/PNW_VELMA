# Create cover permeability layer
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
# Load data
# =======================================================================
# Imports

# ================================
# Stands
stands_path = str(config.cover_type_velma)
cover_key = pd.read_csv(str(config.cover_type_velma.parents[0] / 'cover_type_key.csv'))
stands = np.loadtxt(stands_path, skiprows=6)
outfile = config.cover_type_velma.parents[0] / 'permeability.asc'

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

# Erode NLCD roads by 1 pixel - they look to be about 10-20m, not 30m
road_mask = (nlcd == nlcd_dev_openspace) + (nlcd == nlcd_dev_low)
roads = ndimage.binary_erosion(road_mask, iterations=1)

# Combine CCAP developed with NLCD roads
roads_merge = roads + (ccap == ccap_developed) + (ccap == ccap_dirt)

# Convert to % permeability
perm_fraction = 0.5  # % permeability of roads
perm = np.invert(roads_merge) * 1
perm = np.where(perm == 0, 0.5, perm)

header = readHeader(nlcd_path)
f = open(outfile, "w")
f.write(header)
np.savetxt(f, perm, fmt="%f")
f.close()
