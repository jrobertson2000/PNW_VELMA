# Creates binary filter maps of stands to be affected by a given disturbance
# In VELMA, for each disturbance (e.g. clearcut, 1st trimming, 2nd trimming) the user specifies an integer filter map
# and the integers which will be affected by a disturbance. The exported filter maps from this script have 1 for pixels
# included in a disturbance, 0 for those excluded. User then specifies 1 for 'initializeFilterIds' in disturbance
# parameters.
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import tempfile
from scipy import ndimage
from utils import flowlines
from soil_merger import readHeader
# ======================================================================================================================
# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()

filter_dir = config.stand_id_velma.parents[0] / 'filter_maps'
try:
    filter_dir.mkdir(parents=True)
except FileExistsError:
    pass
# =======================================================================
# WA requires a 10 meter no-management buffer around all streams, so will add those in with ID=0

# Create flowlines raster and buffer it by 1 cell (10m/30ft)
flow = flowlines(config.flowlines)
flow.get_flowlines_ascii(tmp_dir)
no_mgmt_buffer = ndimage.binary_dilation(flow.raster, iterations=1)

# Overlay buffer on cover ID map and export
stand_id_prebuff_path = str(config.stand_id)
stand_id_prebuff = np.loadtxt(stand_id_prebuff_path, skiprows=6)  # Each stand has a different number
stand_id_prebuff[no_mgmt_buffer] = 0

try:
    filter_dir.mkdir(parents=True)
except WindowsError:
    pass
header = readHeader(str(config.dem_velma))
f = open(config.stand_id_velma, "w")
f.write(header)
np.savetxt(f, stand_id_prebuff, fmt="%i")
f.close()


# cover_id is a map of cover_id created in cover_rasterize_stands.py corresponding to stands, no management buffer (0),
# and water/area outside of watershed (1)

stand_id_path = str(config.stand_id_velma)
stand_id = np.loadtxt(stand_id_path, skiprows=6)
# These are the VELMA_IDs of the Ellsworth Experimental Basins
basin_id = pd.read_csv(str(config.stand_id_velma.parents[0] / 'experimental_basin_velma_id.csv'))



# =======================================================================
# Disturbances

# Convert filter_map to list, then loop through and convert pixels to 1 if in stands_include, 0 if excluded
stand_id_list = stand_id.flatten().tolist()
stands = [int(x) for x in np.unique(stand_id)]
header = readHeader(stand_id_path)


def create_filter_map(disturbance_name, include):
    filter_map_list = [1 if x in include else 0 for x in stand_id_list]
    filter_map = np.array(filter_map_list).reshape(stand_id.shape)
    outfile = filter_dir / '{}.asc'.format(disturbance_name)
    f = open(outfile, 'w')
    f.write(header)
    # np.savetxt(f, filter_map, fmt='%i')
    f.close()
    return filter_map

# ===================================
disturbance = 'industrial_clearcut'
# All stands can be cut
stands_exclude = [0, 1]  # Exclude no mgmt buffer (0) and water/area outside watershed (1)
stands_include = [x for x in stands if x not in stands_exclude]
map1 = create_filter_map(disturbance, stands_include)

# ===================================
disturbance = 'active_all'
# All stands can be cut
stands_exclude = [0, 1]  # Exclude no mgmt buffer and water/area outside watershed
stands_include = [x for x in stands if x not in stands_exclude]
map2 = create_filter_map(disturbance, stands_include)

# ===================================
disturbance = 'current'
# All non-basin stands + only active stands in experimental basins can be cut
stands_exclude = basin_id.loc[(basin_id['mgmt'] == 'passive') | (basin_id['mgmt'] == 'control')]['VELMA_ID'].tolist()
stands_exclude.append(0)
stands_exclude.append(1)
stands_include = [x for x in stands if x not in stands_exclude]
map3 = create_filter_map(disturbance, stands_include)
