#
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from soil_merger import readHeader
import tempfile
import importlib
import pyproj
from utils import flowlines
from scipy import ndimage

importlib.reload(config)
# ======================================================================================================================

# Calculated from UMD Hansen Global Forest Change
# Raster where pixel values are year of forest loss
# https://code.earthengine.google.com/abedd30c322f12650b6304b597273e9a
yearly_loss_path = config.yearly_forest_loss_velma

filter_dir = config.cover_id_velma.parents[0] / 'filter_maps'
try:
    filter_dir.mkdir(parents=True)
except FileExistsError:
    pass

yearly_loss = np.loadtxt(yearly_loss_path, skiprows=6)

years = np.unique(yearly_loss).tolist()
years.remove(0)

outfiles = [filter_dir / 'historical_clearcut_{}.asc'.format(2000 + int(year)) for year in years]

header = readHeader(yearly_loss_path)

for i, year in enumerate(years):
    loss = (yearly_loss == year) * 1
    f = open(outfiles[i], "w")
    f.write(header)
    np.savetxt(f, loss, fmt="%i")
    f.close()

# =======================================================================
# Create historical cover age map corresponding to start year
cover_age20_path = config.cover_age_velma
cover_age20 = np.loadtxt(cover_age20_path, skiprows=6)

# Identify ages (at 2020) of pixels that were cut from 2004-2019 to see if ages match up
cut_ages = []
for i, year in enumerate(years):
    loss = (yearly_loss == year)
    cut_ages.append(np.unique(cover_age20[loss]))

# Create array of elapsed time between cut date and 2020
elapsed_time = (np.ones(shape=yearly_loss.shape) * 20) - yearly_loss

# Update and export new cover age map - this is the updated map for 2020 with historical cuts accounted for
changed_pixels = (yearly_loss > 0)
cover_age20_updated = cover_age20.copy()
cover_age20_updated[changed_pixels] = elapsed_time.flatten()[elapsed_time.flatten() != 20]

outfile = config.cover_age_velma.parents[0] / 'cover_age_2020updated.asc'
f = open(outfile, "w")
f.write(header)
np.savetxt(f, cover_age20_updated, fmt="%i")
f.close()

# But a more accurate map is one that adjusts age based on when it starts
# This assumes that a forest pixel is cut at 40 years
start_year = 2004
diff = 2020 - start_year
historical_age = cover_age20_updated - diff
historical_age[historical_age <= 0] = historical_age[historical_age <= 0] + 40

outfile = config.cover_age_velma.parents[0] / 'historical_age_{}.asc'.format(start_year)
f = open(outfile, 'w')
f.write(header)
np.savetxt(f, historical_age, fmt='%i')
f.close()
