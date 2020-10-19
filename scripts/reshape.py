# Formats all input rasters to the same projection, resolution, and extent of the DEM
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
import tempfile
import config as config
import numpy as np
import imp
imp.reload(config)
# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()
temp_gdb = 'temp.gdb'
arcpy.CreateFileGDB_management(temp_dir, temp_gdb)

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
# Clip to study area buffer, reproject, resample rasters if resolution =/= DEM resolution, clip to study area
# =======================================================================

# Fetch study area and buffer
study_area = str(config.study_area)
study_area_buff = temp_dir + '/study_area_buff.shp'
arcpy.Buffer_analysis(in_features=study_area, out_feature_class=study_area_buff, buffer_distance_or_field="15 Kilometers",
                      line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field="", method="PLANAR")

# DEM
try:
    dem_in = temp_dir + '/' + dem_mosaic
except NameError:
    dem_in = str(config.dem)
dem_out = str(config.dem_out)
arcpy.Clip_management(in_raster=dem_in, out_raster=dem_out, in_template_dataset=study_area, nodata_value=-999999, clipping_geometry=True)

# Get DEM cell size and spatial ref for reprojection/resampling of rasters
dem_x = arcpy.GetRasterProperties_management(dem_out, 'CELLSIZEX').getOutput(0)
dem_y = arcpy.GetRasterProperties_management(dem_out, 'CELLSIZEY').getOutput(0)
dem_xy = dem_x + ' ' + dem_y
dem_spatial_ref = arcpy.Describe(dem_out).spatialReference

# Flow accumulation
print 'Prepping flow accumulation ...'
fac_in = str(config.fac)
fac_buff = temp_dir + '/fac_buff.tif'
fac_reproj = temp_dir + '/fac_reproj.tif'
fac_out = str(config.fac_out)
arcpy.Clip_management(in_raster=fac_in, out_raster=fac_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=fac_buff, out_raster=fac_reproj, out_coor_system=dem_spatial_ref, resampling_type='BILINEAR',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=fac_reproj, out_raster=fac_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.fac_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# NLCD
print 'Prepping NLCD ...'
nlcd_in = str(config.nlcd)
nlcd_buff = temp_dir + '/nlcd_buff.tif'
nlcd_reproj = temp_dir + '/nlcd_reproj.tif'
nlcd_out = str(config.nlcd_out)
arcpy.Clip_management(in_raster=nlcd_in, out_raster=nlcd_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=nlcd_buff, out_raster=nlcd_reproj, out_coor_system=dem_spatial_ref, resampling_type='NEAREST',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=nlcd_reproj, out_raster=nlcd_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.nlcd_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# gSSURGO soil map
print 'Prepping soil ...'
soil_in = str(config.soil)
soil_buff = temp_dir + '/soil_buff.tif'
soil_reproj = temp_dir + '/soil_reproj.tif'
soil_out = str(config.soil_out)
arcpy.Clip_management(in_raster=soil_in, out_raster=soil_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=soil_buff, out_raster=soil_reproj, out_coor_system=dem_spatial_ref, resampling_type='NEAREST',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=soil_reproj, out_raster=soil_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.soil_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# Biomass
print 'Prepping biomass ...'
try:
    biomass_in = temp_dir + '/' + biomass_mosaic
except NameError:
    biomass_in = str(config.biomass)
biomass_buff = temp_dir + '/biomass_buff.tif'
biomass_reproj = temp_dir + '/biomass_reproj.tif'
biomass_out = str(config.biomass_out)
arcpy.Clip_management(in_raster=biomass_in, out_raster=biomass_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=biomass_buff, out_raster=biomass_reproj, out_coor_system=dem_spatial_ref, resampling_type='BILINEAR',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=biomass_reproj, out_raster=biomass_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.biomass_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# Impervious surfaces
print 'Prepping imperv ...'
try:
    imperv_in = temp_dir + '/' + imperv_mosaic
except NameError:
    imperv_in = str(config.imperv)
imperv_buff = temp_dir + '/imperv_buff.tif'
imperv_reproj = temp_dir + '/imperv_reproj.tif'
imperv_out = str(config.imperv_out)
arcpy.Clip_management(in_raster=imperv_in, out_raster=imperv_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=imperv_buff, out_raster=imperv_reproj, out_coor_system=dem_spatial_ref, resampling_type='BILINEAR',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=imperv_reproj, out_raster=imperv_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.imperv_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# PRISM temperature
print 'Prepping PRISM temp ...'
prism_temp_in = str(config.prism_temp)
prism_temp_buff = temp_dir + '/prism_temp_buff.tif'
prism_temp_reproj = temp_dir + '/prism_temp_reproj.tif'
prism_temp_out = str(config.prism_temp_out)
arcpy.Clip_management(in_raster=prism_temp_in, out_raster=prism_temp_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=prism_temp_buff, out_raster=prism_temp_reproj, out_coor_system=dem_spatial_ref, resampling_type='BILINEAR',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=prism_temp_reproj, out_raster=prism_temp_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.prism_temp_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# PRISM precipitation
print 'Prepping PRISM precip ...'
prism_precip_in = str(config.prism_precip)
prism_precip_buff = temp_dir + '/prism_precip_buff.tif'
prism_precip_reproj = temp_dir + '/prism_precip_reproj.tif'
prism_precip_out = str(config.prism_precip_out)
arcpy.Clip_management(in_raster=prism_precip_in, out_raster=prism_precip_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=prism_precip_buff, out_raster=prism_precip_reproj, out_coor_system=dem_spatial_ref, resampling_type='BILINEAR',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=prism_precip_reproj, out_raster=prism_precip_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.prism_precip_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# Cover ID
print 'Prepping cover ID ...'
cover_id_in = str(config.cover_id)
cover_id_buff = temp_dir + '/cover_id_buff.tif'
cover_id_reproj = temp_dir + '/cover_id_reproj.tif'
cover_id_out = str(config.cover_id_out)
arcpy.Clip_management(in_raster=cover_id_in, out_raster=cover_id_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=cover_id_buff, out_raster=cover_id_reproj, out_coor_system=dem_spatial_ref, resampling_type='NEAREST',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=cover_id_reproj, out_raster=cover_id_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.cover_id_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# Cover age
print 'Prepping cover age ...'
cover_age_in = str(config.cover_age)
cover_age_buff = temp_dir + '/cover_age_buff.tif'
cover_age_reproj = temp_dir + '/cover_age_reproj.tif'
cover_age_out = str(config.cover_age_out)
arcpy.Clip_management(in_raster=cover_age_in, out_raster=cover_age_buff, in_template_dataset=study_area_buff, clipping_geometry=True)
arcpy.ProjectRaster_management(in_raster=cover_age_buff, out_raster=cover_age_reproj, out_coor_system=dem_spatial_ref, resampling_type='NEAREST',
                               cell_size=dem_xy)
arcpy.Clip_management(in_raster=cover_age_reproj, out_raster=cover_age_out, in_template_dataset=study_area, clipping_geometry=True)
size = np.round((config.cover_age_out.stat().st_size / 10e6), 2)
print 'File size: ', size, ' MB'

# Heat load index: calculate for study area
arcpy.ImportToolbox(str(config.geomorph_tbx_path))
arcpy.hli(Select_DEM=dem_out, HLI_Output_Raster="C:/Users/ipdavies/tnc_velma/data/topography/ellsworth/hli_ells.tif")



