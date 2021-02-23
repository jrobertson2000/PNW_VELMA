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
# Convert and merge landcover classes

# Stand class values
bare_id = cover_key.loc[cover_key['type'] == 'BARE', 'id'].iloc[0]
bpa_id = cover_key.loc[cover_key['type'] == 'BPA', 'id'].iloc[0]
nf_id = cover_key.loc[cover_key['type'] == 'NF', 'id'].iloc[0]
conifer_id = cover_key.loc[cover_key['type'] == 'conifer', 'id'].iloc[0]

# Replace CCAP developed and dirt with conifer
ccap[(ccap == ccap_developed)] = conifer_id

# Replace CCAP forest with conifer
ccap[(ccap == ccap_forest)] = conifer_id

# Replace bare, bpa, and nf that were in stands with conifer
ccap[(ccap == bare_id)] = conifer_id
ccap[(ccap == bpa_id)] = conifer_id
ccap[(ccap == nf_id)] = conifer_id

# Overlay NLCD deciduous forests on CCAP
ccap[(nlcd == nlcd_forest_decid)] = nlcd_forest_decid

# Replace CCAP shrub, herbaceous, dirt, and water with conifer
ccap[(ccap == ccap_herby)] = conifer_id
ccap[(ccap == ccap_shrub)] = conifer_id
ccap[(ccap == ccap_dirt)] = conifer_id
ccap[(ccap == ccap_water)] = conifer_id

header = readHeader(stands_path)
f = open(outfile, "w")
f.write(header)
np.savetxt(f, ccap, fmt="%i")
f.close()

# Create cover type map that is just conifer
conifer = (ccap * 0) + 1
outfile = config.cover_type_ccap_merge_velma.parents[0] / 'conifer.asc'
f = open(outfile, "w")
f.write(header)
np.savetxt(f, conifer, fmt='%i')
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
