# Formats all input rasters to the same projection, resolution, and extent of the DEM
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
import tempfile
import config as config
import numpy as np
import imp
imp.reload(config)
arcpy.CheckOutExtension('Spatial')
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
# Set up functions
# =======================================================================

class getROI:
    def __init__(self, roi, dem_in):
        self.roi = roi
        self.roi_buff = temp_dir + '/roi_buff.shp'
        self.roi_reproj = temp_dir + '/roi_reproj.shp'
        
        arcpy.Project_management(in_dataset=roi, out_dataset=self.roi_reproj, out_coor_system=arcpy.Describe(dem_in).spatialReference)
        arcpy.CopyFeatures_management(self.roi_reproj, roi)
        arcpy.Buffer_analysis(in_features=roi, out_feature_class=self.roi_buff,
                              buffer_distance_or_field="15 Kilometers",
                              line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field="",
                              method="PLANAR")
        


class getDEMspecs:
    """ Get DEM cell size and spatial ref for reprojection/resampling of rasters """
    def __init__(self, dem_out):
        self.dem = dem_out
        self.x = arcpy.GetRasterProperties_management(dem_out, 'CELLSIZEX').getOutput(0)
        self.y = arcpy.GetRasterProperties_management(dem_out, 'CELLSIZEY').getOutput(0)
        self.xy = self.x + ' ' + self.y
        self.spatial_ref = arcpy.Describe(dem_out).spatialReference
        self.extent = arcpy.sa.Raster(dem_out).extent


def reshape(in_path, out_path, name, resamp_type, dem_specs, temp_dir, roi_layers):
    print 'Prepping ' + name + ' ...'
    file_in = str(in_path)
    buff = temp_dir + '/buff.tif'
    reproj = temp_dir + '/reproj.tif'
    file_out = str(out_path)
    arcpy.Clip_management(in_raster=file_in, out_raster=buff, in_template_dataset=roi_layers.roi_buff,
                          clipping_geometry=True)
    arcpy.ProjectRaster_management(in_raster=buff, out_raster=reproj, out_coor_system=dem_specs.spatial_ref,
                                   resampling_type=resamp_type,
                                   cell_size=dem_specs.xy)
    envelope = '{} {} {} {}'.format(dem_specs.extent.XMin, dem_specs.extent.YMin, dem_specs.extent.XMax, dem_specs.extent.YMax)
    arcpy.Clip_management(in_raster=reproj, out_raster=file_out, rectangle=envelope, nodata_value=-9999)
    print'Done'

# =======================================================================
# Clip to study area buffer, reproject, resample rasters
# =======================================================================

# Fetch study area and buffer
try:
    dem_in = temp_dir + '/' + dem_mosaic
except NameError:
    dem_in = str(config.dem)

dem_out = str(config.dem_out)
dem_spatialref = arcpy.Describe(dem_in).spatialReference

roi = str(config.study_area)
roi_layers = getROI(roi, dem_in)
arcpy.Clip_management(in_raster=dem_in, out_raster=dem_out, in_template_dataset=roi_layers.roi, nodata_value=-9999, clipping_geometry=True)

dem_specs = getDEMspecs(dem_out)

# gSSURGO map
reshape(config.gssurgo, config.gssurgo_out, 'gSSURGO', 'NEAREST', dem_specs, temp_dir, roi_layers)

# STATSGO2 map
reshape(config.statsgo2, config.statsgo2_out, 'STATSGO2', 'NEAREST', dem_specs, temp_dir, roi_layers)

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

# Heat load index: calculate for study area
arcpy.ImportToolbox(str(config.geomorph_tbx_path))
arcpy.hli(Select_DEM=dem_out, HLI_Output_Raster="C:/Users/ipdavies/tnc_velma/data/topography/ellsworth/hli_ells.tif")



