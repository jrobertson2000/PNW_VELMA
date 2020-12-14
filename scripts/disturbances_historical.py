#
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import rasterio
from rasterio.plot import reshape_as_image, reshape_as_raster
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

with rasterio.open(yearly_loss_path, 'r') as src:
    yearly_loss = reshape_as_image(src.read()).squeeze()

years = np.unique(yearly_loss)
outfiles = [filter_dir / 'historical_clearcut_{}.asc'.format(2000 + year) for year in years]

header = readHeader(yearly_loss_path)

for i, year in enumerate(years):
    loss = (yearly_loss == year) * 1
    f = open(outfiles[i], "w")
    f.write(header)
    np.savetxt(f, loss, fmt="%i")
    f.close()

# =======================================================================


