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
from soil.soil_merger import readHeader
# ======================================================================================================================
# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()

# cover_id is a map of cover_ids created in cover_rasterize_stands.py corresponding to stands, no management buffer (0),
# and water/area outside of watershed (1)
filter_dir = config.cover_id_velma.parents[0] / 'filter_maps'
try:
    filter_dir.mkdir(parents=True)
except FileExistsError:
    pass
cover_id_path = str(filter_dir / 'filtermap.asc')
cover_id = np.loadtxt(cover_id_path, skiprows=6)
# These are the VELMA_IDs of the Ellsworth Experimental Basins
basin_ids = pd.read_csv(str(config.cover_id_velma.parents[0] / 'experimental_basin_velma_id.csv'))



# =======================================================================
# Disturbances

# Convert filter_map to list, then loop through and convert pixels to 1 if in stands_include, 0 if excluded
cover_id_list = cover_id.flatten().tolist()
stands = [int(x) for x in np.unique(cover_id)]
header = readHeader(cover_id_path)


def create_filter_map(disturbance_name, exclude, include):
    filter_map_list = [1 if x in stands_include else 0 for x in cover_id_list]
    filter_map = np.array(filter_map_list).reshape(cover_id.shape)
    outfile = filter_dir / '{}.asc'.format(disturbance_name)
    f = open(outfile, 'w')
    f.write(header)
    np.savetxt(f, filter_map, fmt='%i')
    f.close()
    return filter_map

# ===================================
disturbance = 'industrial_clearcut'
# All stands can be cut
stands_exclude = [0, 1]  # Exclude no mgmt buffer (0) and water/area outside watershed (1)
stands_include = [x for x in stands if x not in stands_exclude]
map1 = create_filter_map(disturbance, stands_exclude, stands_include)

# ===================================
disturbance = 'active_all'
# All stands can be cut
stands_exclude = [0, 1]  # Exclude no mgmt buffer and water/area outside watershed
stands_include = [x for x in stands if x not in stands_exclude]
map2 = create_filter_map(disturbance, stands_exclude, stands_include)

# ===================================
disturbance = 'current'
# All non-basin stands + only active stands in experimental basins can be cut
stands_exclude = basin_ids.loc[(basin_ids['mgmt'] == 'passive') | (basin_ids['mgmt'] == 'control')]['VELMA_ID'].tolist()
stands_exclude.append(0)
stands_exclude.append(1)
stands_include = [x for x in stands if x not in stands_exclude]
map3 = create_filter_map(disturbance, stands_exclude, stands_include)
