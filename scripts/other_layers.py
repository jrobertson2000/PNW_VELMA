# Formats all input rasters to the same projection, resolution, and extent of the DEM
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
import tempfile
import config as config
import imp
from utils import reshape, getDEMspecs, getROI
imp.reload(config)
arcpy.CheckOutExtension('Spatial')
# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

# =======================================================================
# Mosaic rasters
# =======================================================================

# Mosaic DEMs
try:
    dem_list = [str(x) for x in config.dem_list]
    dem_mosaic = 'dem_mosaic.tif'
    arcpy.MosaicToNewRaster_management(input_rasters=dem_list, output_location=temp_dir,
                                       raster_dataset_name_with_extension=dem_mosaic, pixel_type='32_BIT_SIGNED',
                                       number_of_bands=1)
except AttributeError:
    pass

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
try:
    dem_in = temp_dir + '/' + dem_mosaic
except NameError:
    dem_in = str(config.dem)

roi = str(config.study_area)
dem_in = str(config.dem)
dem_out = str(config.dem_out)
roi_layers = getROI(roi, dem_in, temp_dir)

arcpy.Clip_management(in_raster=dem_in, out_raster=dem_out, in_template_dataset=roi_layers.roi, nodata_value=-9999,
                      clipping_geometry=True)
dem_specs = getDEMspecs(dem_out)

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

# PRISM temperature
reshape(config.prism_temp, config.prism_temp_out, 'prism_temp', 'BILINEAR', dem_specs, temp_dir, roi_layers)

# PRISM precipitation
reshape(config.prism_precip, config.prism_precip_out, 'prism_precip', 'BILINEAR', dem_specs, temp_dir, roi_layers)

# Cover ID
reshape(config.cover_id, config.cover_id_out, 'cover_id', 'NEAREST', dem_specs, temp_dir, roi_layers)

# Cover age
reshape(config.cover_age, config.cover_age_out, 'cover_age', 'NEAREST', dem_specs, temp_dir, roi_layers)

# Cover type
reshape(config.cover_type, config.cover_type_out, 'cover_type', 'NEAREST', dem_specs, temp_dir, roi_layers)
