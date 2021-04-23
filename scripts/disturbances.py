# Creates binary filter maps of stands to be affected by a given disturbance
# In VELMA, for each disturbance (e.g. clearcut, 1st trimming, 2nd trimming) the user specifies an integer filter map
# and the integers which will be affected by a disturbance. The exported filter maps from this script have 1 for pixels
# included in a disturbance, 0 for those excluded. User then specifies 1 for 'initializeFilterIds' in disturbance
# parameters.
# Script written in Python 3.7

import config as config
import numpy as np
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

# Overlay buffer on stand ID map
stand_id_path = str(config.stand_id_velma)
stand_id = np.loadtxt(stand_id_path, skiprows=6)  # Each stand has a different number
stand_id[stand_id == -9999] = np.nan
stand_id[no_mgmt_buffer] = 0

# Import map of the Ellsworth Experimental Basins. Passive=0, Control=1, Active=2
exp_basins = np.loadtxt(config.exp_basins_velma, skiprows=6)
exp_basins[exp_basins == -9999] = np.nan

# Marbled murrelet habitat is a protected area that can't be harvested
murrelet = np.loadtxt(config.data_path / 'landcover' / 'murrelet_no_harvest.asc', skiprows=6)
murrelet[murrelet == -9999] = np.nan

# =======================================================================
# Create (binary) disturbance filter maps for each forest management scenario

# ===================================
disturbance = 'industrial_clearcut'
# All stands can be cut except protected areas
filter_map = ((stand_id == 0) + (murrelet == 1))  # The excluded cells here are TRUE
filter_map = np.invert(filter_map) * 1  # TRUE cells are inverted to false, and then binarized
outfile = filter_dir / '{}.asc'.format(disturbance)
f = open(outfile, 'w')
header = readHeader(stand_id_path)
f.write(header)
np.savetxt(f, filter_map, fmt='%i')
f.close()

# ===================================
disturbance = 'active_all'
# All stands can be cut except protected areas
filter_map = ((stand_id == 0) + (murrelet == 1))
filter_map = np.invert(filter_map) * 1
outfile = filter_dir / '{}.asc'.format(disturbance)
f = open(outfile, 'w')
header = readHeader(stand_id_path)
f.write(header)
np.savetxt(f, filter_map, fmt='%i')
f.close()

# ===================================
disturbance = 'baseline'
# Active experimental basins and all stands outside of basins can be cut, except protected areas
filter_map = ((stand_id == 0) + (murrelet == 1) + (exp_basins == 1) + (exp_basins == 2))
filter_map = np.invert(filter_map) * 1
outfile = filter_dir / '{}.asc'.format(disturbance)
f = open(outfile, 'w')
header = readHeader(stand_id_path)
f.write(header)
np.savetxt(f, filter_map, fmt='%i')
f.close()

