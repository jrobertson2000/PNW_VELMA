# Checks file extent and presence of NoData cells in ASCII files
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import tempfile
from rasterio import features
from pathlib import Path
import matplotlib.pyplot as plt
from soil_merger import readHeader
import importlib
importlib.reload(config)

# ======================================================================================================================

# =======================================================================
# Check for file extent and NoData cells
# =======================================================================

velma_file_paths = [config.dem_velma, config.fac_velma, config.cover_type_merge_velma, config.cover_age_velma,
                    config.cover_id_velma, config.soil_velma]

dem_file = config.dem_velma
size = np.loadtxt(str(dem_file), skiprows=6).shape

print('Checking file extent')
for path in velma_file_paths:
    file = np.loadtxt(str(path), skiprows=6)
    if file.shape != size:
        print('Shape mismatch: {} in {}'.format(file.shape, path))
    with rasterio.open(path, 'r') as src:
        nodata_val = src.nodatavals[0]
    if nodata_val in file:
        print('NoData value of {} in {}'.format(nodata_val, path))

