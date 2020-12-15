# Formats NLCD raster to the same projection, resolution, and extent of the DEM
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
temp_dir = tempfile.mkdtemp()

# Set environment settings
env.workspace = temp_dir  # Set to temp so that rasters created during velma_format are deleted
arcpy.env.overwriteOutput = True

# =======================================================================
# Clip to study area buffer, reproject, resample rasters
# =======================================================================

# Fetch study area and buffer
roi = str(config.study_area)
dem_velma = str(config.dem_velma)
roi_layers = getROI(roi, dem_velma, temp_dir)

dem_specs = getDEMspecs(dem_velma)

# NLCD Land Cover
reshape(config.nlcd, config.nlcd_out, 'nlcd_landcover', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.nlcd_out, config.nlcd_velma)

# NOAA C-CAP
reshape(config.noaa_ccap, config.noaa_ccap_out, 'noaa_ccap', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.noaa_ccap_out, config.noaa_ccap_velma)

# NLCD Impervious
reshape(config.imperv, config.imperv_out, 'nlcd_imperv', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.imperv_out, config.imperv_velma)