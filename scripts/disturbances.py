# Creates disturbance maps for harvest scenarios
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import importlib
from utils import flowlines
from scipy import ndimage
importlib.reload(config)
# ======================================================================================================================

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

# =======================================================================
# Create disturbance maps from stand rasters
# For each scenario (e.g. clearcut, 1st trimming, 2nd trimming) there needs to be a binary filter map that
# designates which cells are affected by the disturbance. Each stand will have the same filter value. The filter map is
# created by supplying a text file with the VELMA_IDs that will be affected by the disturbance. For Ellsworth, a 10m
# no-management buffer is applied around streams for all scenarios.
# =======================================================================

cover_ids = np.loadtxt(str(config.cover_id_velma), skiprows=6)  # Each stand has a different number
# These are the VELMA_IDs of the Ellsworth Experimental Basins
basin_ids = pd.read_csv(str(config.cover_id_velma.parents[0] / 'experimental_basin_velma_id.csv'))

dist_names = ['current']

outdir = config.cover_id_velma.parents[0] / 'filter_maps'
try:
    outdir.mkdir(parents=True)
except FileExistsError:
    pass

# Create flowlines raster and buffer it by 1 cell (10m/30ft)
flow = flowlines(config.flowlines)
flow.get_flowlines_ascii(temp_dir)
no_mgmt_buffer = ndimage.binary_dilation(flow.raster, iterations=1)

# Create list of stands that will be excluded from disturbance
no_mgmt_stands = basin_ids.loc[(basin_ids['mgmt'] == 'passive') | (basin_ids['mgmt'] == 'control')]['VELMA_ID'].tolist()

for i, dist_name in enumerate(dist_names):
    filter_map = ~np.isin(cover_ids, no_mgmt_stands) * 1  # 1=disturbance, 0=no disturbance
    filter_map[no_mgmt_buffer] = 0
    # plt.imshow(filter_map)
    outfile = outdir / '{}_filter.asc'.format(dist_name)
    flow.raster_header
    f = open(outfile, 'w')
    f.write(flow.raster_header)
    np.savetxt(f, filter_map, fmt='%i')
    f.close()

