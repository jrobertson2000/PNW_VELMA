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

outfiles = [filter_dir / 'historical_clearcut_{}.asc'.format(2000 + year) for year in years]

header = readHeader(yearly_loss_path)

for i, year in enumerate(years):
    loss = (yearly_loss == year) * 1
    f = open(outfiles[i], "w")
    f.write(header)
    np.savetxt(f, loss, fmt="%i")
    f.close()
