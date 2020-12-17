# Creates CSV with filter map IDs of stands to be affected by a given disturbance
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import importlib
import pyproj
from utils import flowlines
from scipy import ndimage

importlib.reload(config)
# ======================================================================================================================

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

# =======================================================================
# For each disturbance (e.g. clearcut, 1st trimming, 2nd trimming) the user specifies an integer filter map and the
# integers which will be affected by a disturbance. Each stand in the filter map has a unique value, with a 30ft no
# management buffer around streams with a value of 0.
#
# This script exports a CSV with the integers that are selected for each disturbance, which can be entered into the
# VELMA GUI.
# =======================================================================

filter_map_path = str(config.cover_id_velma.parents[0] / 'filtermap.asc')
filter_map = np.loadtxt(filter_map_path, skiprows=6)
# These are the VELMA_IDs of the Ellsworth Experimental Basins
basin_ids = pd.read_csv(str(config.cover_id_velma.parents[0] / 'experimental_basin_velma_id.csv'))

filter_dir = config.cover_id_velma.parents[0] / 'filter_maps'
try:
    filter_dir.mkdir(parents=True)
except FileExistsError:
    pass

stands = [int(x) for x in np.unique(filter_map)]

# =======================================================================
# Disturbances
disturbance_stands = []
disturbances = []

# ===================================
disturbance = 'industrial_clearcut'
# All stands can be cut
stands_exclude = [0, 1]  # Exclude no mgmt buffer and water/area outside watershed
stands_include = [x for x in stands if x not in stands_exclude]
disturbance_stands.append(stands_include)
disturbances.append(disturbance)

# ===================================
disturbance = 'active_all'
# All stands can be cut
stands_exclude = [0, 1]  # Exclude no mgmt buffer and water/area outside watershed
stands_include = [x for x in stands if x not in stands_exclude]
disturbance_stands.append(stands_include)
disturbances.append(disturbance)

# ===================================
disturbance = 'current'
# All non-basin stands + only active stands in experimental basins can be cut
stands_exclude = basin_ids.loc[(basin_ids['mgmt'] == 'passive') | (basin_ids['mgmt'] == 'control')]['VELMA_ID'].tolist()
stands_exclude.append(0)
stands_exclude.append(1)
stands_include = [x for x in stands if x not in stands_exclude]
disturbance_stands.append(stands_include)
disturbances.append(disturbance)

# Combine all the disturbances together
df = pd.DataFrame({'disturbance': disturbances, 'ids': disturbance_stands})

# Export
df['ids'] = df['ids'].astype('string')
df['ids'] = df['ids'].map(lambda x: x.lstrip('[]').rstrip('aAbBcC'))
df.to_csv(str(filter_dir / 'disturbance_filter_ids.csv'), index=False)


# # Create list of stands that will be excluded from disturbance
stands_exclude = basin_ids.loc[(basin_ids['mgmt'] == 'passive') | (basin_ids['mgmt'] == 'control')]['VELMA_ID'].tolist()

# for i, dist_name in enumerate(dist_names):
#     filter_map = ~np.isin(cover_ids, no_mgmt_stands) * 1  # 1=disturbance, 0=no disturbance
#     filter_map[no_mgmt_buffer] = 0
#     # plt.imshow(filter_map)
#     outfile = outdir / '{}_filter.asc'.format(dist_name)
#     flow.raster_header
#     f = open(outfile, 'w')
#     f.write(flow.raster_header)
#     np.savetxt(f, filter_map, fmt='%i')
#     f.close()


# Create a map of stand IDs

