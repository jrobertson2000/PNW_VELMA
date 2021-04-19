# Formats cover source rasters (NLCD, CCAP, etc.) to the same projection, resolution, and extent of the DEM
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
import tempfile
import config as config
import imp
from utils import reshape, getDEMspecs, getROI, velma_format
imp.reload(config)
arcpy.CheckOutExtension('Spatial')
# ======================================================================================================================
# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()

# Set environment settings
env.workspace = tmp_dir  # Set to temp so that rasters created during velma_format are deleted
arcpy.env.overwriteOutput = True

# =======================================================================
# Clip to study area buffer, reproject, resample rasters
# =======================================================================

# Fetch study area and buffer
cell_size = config.cell_size
proj = str(config.proj_wkt)
roi = str(config.study_area)
dem_velma = str(config.dem_velma)
roi_layers = getROI(roi, tmp_dir, proj)

dem_specs = getDEMspecs(dem_velma)

# NLCD Land Cover
nlcd_tmp = tmp_dir + '/nlcd.tif'
reshape(config.nlcd, nlcd_tmp, 'nlcd_landcover', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
try:
    config.nlcd_velma.parents[0].mkdir(parents=True)
except WindowsError:
    pass
velma_format(nlcd_tmp, config.nlcd_velma)


# NOAA C-CAP
ccap_tmp = tmp_dir + '/ccap.tif'
reshape(config.noaa_ccap, ccap_tmp, 'noaa_ccap', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
try:
    config.noaa_ccap_velma.parents[0].mkdir(parents=True)
except WindowsError:
    pass
velma_format(ccap_tmp, config.noaa_ccap_velma)