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
temp_dir = tempfile.mkdtemp()

# Set environment settings
env.workspace = temp_dir  # Set to temp so that rasters created during velma_format are deleted
arcpy.env.overwriteOutput = True

# =======================================================================
# Mosaic rasters
# =======================================================================

# Mosaic biomass
try:
    biomass_list = [str(x) for x in config.biomass_list]
    biomass_mosaic = 'biomass_mosaic.tif'
    arcpy.MosaicToNewRaster_management(input_rasters=biomass_list, output_location=temp_dir,
                                       raster_dataset_name_with_extension=biomass_mosaic, pixel_type='32_BIT_SIGNED',
                                       number_of_bands=1)
except AttributeError:
    pass

# Mosaic imperv
try:
    imperv_list = [str(x) for x in config.imperv_list]
    imperv_mosaic = 'imperv__mosaic.tif'
    arcpy.MosaicToNewRaster_management(input_rasters=imperv_list, output_location=temp_dir,
                                       raster_dataset_name_with_extension=imperv_mosaic, pixel_type='32_BIT_SIGNED',
                                       number_of_bands=1)
except AttributeError:
    pass

# =======================================================================
# Clip to study area buffer, reproject, resample rasters
# =======================================================================

# Fetch study area and buffer
roi = str(config.study_area)
dem_velma = str(config.dem_velma)
roi_layers = getROI(roi, dem_velma, temp_dir)

dem_specs = getDEMspecs(dem_velma)

# # NLCD
# reshape(config.nlcd, config.nlcd_out, 'nlcd', 'NEAREST', temp_dir, roi_layers)

# # Biomass
# try:
#     biomass = temp_dir + '/' + biomass_mosaic
# except NameError:
#     biomass = str(config.biomass)
# reshape(config.biomass, config.biomass_out, 'biomass', 'NEAREST', temp_dir, roi_layers)

# Impervious surfaces
try:
    imperv = temp_dir + '/' + imperv_mosaic
except NameError:
    imperv = str(config.imperv)
reshape(config.imperv, config.imperv_out, 'imperv', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.imperv_out, config.imperv_velma)

# PRISM temperature
reshape(config.prism_temp, config.prism_temp_out, 'prism_temp', 'BILINEAR', dem_specs, temp_dir, roi_layers)
velma_format(config.prism_temp_out, config.prism_temp_velma)

# PRISM precipitation
reshape(config.prism_precip, config.prism_precip_out, 'prism_precip', 'BILINEAR', dem_specs, temp_dir, roi_layers)
velma_format(config.prism_precip_out, config.prism_precip_velma)

# Cover ID
reshape(config.cover_id, config.cover_id_out, 'cover_id', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.cover_id_out, config.cover_id_velma)

# Cover age
reshape(config.cover_age, config.cover_age_out, 'cover_age', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.cover_age_out, config.cover_age_velma)

# Cover type
reshape(config.cover_type, config.cover_type_out, 'cover_type', 'NEAREST', dem_specs, temp_dir, roi_layers)
velma_format(config.cover_type_out, config.cover_type_velma)
