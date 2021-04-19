# Formats all input rasters to the same projection, resolution, and extent of the DEM
# Script written in Python 2.7, not compatible with Python 3

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
proj = str(config.proj_wkt)
cell_size = config.cell_size
roi = str(config.study_area)
dem_velma = str(config.dem_velma)
roi_layers = getROI(roi, tmp_dir, proj)

dem_specs = getDEMspecs(dem_velma)

# Cover age
cover_age_tmp = tmp_dir + '/cover_age.tif'
reshape(config.cover_age, cover_age_tmp, 'cover_age', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
velma_format(cover_age_tmp, config.cover_age_velma)

# Cover type
cover_type_tmp = tmp_dir + '/cover_type.tif'
reshape(config.cover_type, cover_type_tmp, 'cover_type', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
velma_format(cover_type_tmp, config.cover_type_velma)

# Global Forest Loss (yearly)
yearly_forest_loss_tmp = tmp_dir + '/yearly_forest_loss.tif'
reshape(config.yearly_forest_loss, yearly_forest_loss_tmp, 'yearly_forest_loss', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
velma_format(yearly_forest_loss_tmp, config.yearly_forest_loss_velma)






