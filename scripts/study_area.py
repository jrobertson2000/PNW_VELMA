# Create binary mask of study area for VELMA delineation and allows user to identify outpour point graphically
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import tempfile
from rasterio import features
from pathlib import Path
from utils import flowlines
import matplotlib.pyplot as plt
import importlib
importlib.reload(config)
# ======================================================================================================================

temp_dir = tempfile.mkdtemp()

# =======================================================================
# Rasterize study area and convert to binary mask
# =======================================================================
roi = gpd.read_file(config.study_area)
cols = roi.columns.to_list()
cols.remove('geometry')
roi = roi.drop(cols, axis=1)
roi['value'] = 1

dem_file = str(config.dem_velma)

roi_raster = config.dem_velma.parents[1] / 'roi.asc'

# Take DEM and set all values to NaN, then burn species shp into empty DEM raster
with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = 0
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(roi_raster, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(roi.geometry, roi.value))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)

roi_asc = np.loadtxt(roi_raster, skiprows=6)


# =======================================================================
# Overlay rasters and find outpour point
# =======================================================================
flow = flowlines(config.flowlines)
flow.get_flowlines_ascii(temp_dir)
flow.raster[flow.raster == 0] = np.nan

plt.imshow(roi_asc, aspect='equal')
plt.imshow(flow.raster, aspect='equal')

# NOTE: plt.imshow() is plotted such that the pixel centers are full integers, not the edges. So go to the quadrant 3
# (clockwise from top left) of a pixel and round down to get integer row/col coordinates.
# E.g. 280.34, 179.405 round down to 280, 179