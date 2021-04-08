# Formats all input rasters to the same projection, resolution, and extent of the DEM
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
# Mosaic rasters
# =======================================================================

# Mosaic biomass
try:
    biomass_list = [str(x) for x in config.biomass_list]
    biomass_mosaic = 'biomass_mosaic.tif'
    arcpy.MosaicToNewRaster_management(input_rasters=biomass_list, output_location=tmp_dir,
                                       raster_dataset_name_with_extension=biomass_mosaic, pixel_type='32_BIT_SIGNED',
                                       number_of_bands=1)
except AttributeError:
    pass

# Mosaic imperv
try:
    imperv_list = [str(x) for x in config.imperv_list]
    imperv_mosaic = 'imperv__mosaic.tif'
    arcpy.MosaicToNewRaster_management(input_rasters=imperv_list, output_location=tmp_dir,
                                       raster_dataset_name_with_extension=imperv_mosaic, pixel_type='32_BIT_SIGNED',
                                       number_of_bands=1)
except AttributeError:
    pass

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

# # Biomass
# try:
#     biomass = tmp_dir + '/' + biomass_mosaic
# except NameError:
#     biomass = str(config.biomass)
# reshape(config.biomass, config.biomass_out, 'biomass', 'NEAREST', tmp_dir, roi_layers)

# # Impervious surfaces
# try:
#     imperv = tmp_dir + '/' + imperv_mosaic
# except NameError:
#     imperv = str(config.imperv)
# imperv_tmp = tmp_dir / 'imperv.tif'
# reshape(config.imperv, imperv_tmp, 'imperv', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
# velma_format(imperv_tmp, config.imperv_velma)

# Cover ID
cover_id_tmp = tmp_dir + '/cover_id.tif'
reshape(config.cover_id, cover_id_tmp, 'cover_id', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
velma_format(cover_id_tmp, config.cover_id_velma)

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






