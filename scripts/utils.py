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


class getROI:
    def __init__(self, roi, dem_in, temp_dir):
        self.roi = roi
        self.roi_buff = temp_dir + '/roi_buff.shp'
        self.roi_reproj = temp_dir + '/roi_reproj.shp'

        arcpy.Project_management(in_dataset=roi, out_dataset=self.roi_reproj,
                                 out_coor_system=arcpy.Describe(dem_in).spatialReference)
        arcpy.CopyFeatures_management(self.roi_reproj, roi)
        arcpy.Buffer_analysis(in_features=roi, out_feature_class=self.roi_buff,
                              buffer_distance_or_field="15 Kilometers",
                              line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field="",
                              method="PLANAR")


class getDEMspecs:
    """ Get DEM cell size and spatial ref for reprojection/resampling of rasters """

    def __init__(self, dem_velma):
        self.dem = dem_velma
        self.x = arcpy.GetRasterProperties_management(dem_velma, 'CELLSIZEX').getOutput(0)
        self.y = arcpy.GetRasterProperties_management(dem_velma, 'CELLSIZEY').getOutput(0)
        self.xy = self.x + ' ' + self.y
        self.spatial_ref = arcpy.Describe(dem_velma).spatialReference
        self.extent = arcpy.sa.Raster(dem_velma).extent


def reshape(in_path, out_path, name, resamp_type, dem_specs, temp_dir, roi_layers):
    print 'Prepping ' + name + ' ...'
    arcpy.env.snapRaster = dem_specs.dem
    file_in = str(in_path)
    buff = temp_dir + '/buff.tif'
    reproj = temp_dir + '/reproj.tif'
    file_out = str(out_path)
    arcpy.Clip_management(in_raster=file_in, out_raster=buff, in_template_dataset=roi_layers.roi_buff,
                          clipping_geometry=True)
    arcpy.ProjectRaster_management(in_raster=buff, out_raster=reproj, out_coor_system=dem_specs.spatial_ref,
                                   resampling_type=resamp_type,
                                   cell_size=dem_specs.xy)
    envelope = '{} {} {} {}'.format(dem_specs.extent.XMin, dem_specs.extent.YMin, dem_specs.extent.XMax,
                                    dem_specs.extent.YMax)
    arcpy.Clip_management(in_raster=reproj, out_raster=file_out, rectangle=envelope, nodata_value=-9999)
    print'Done'


def velma_format(in_file, out_file):
    # Replace NoData values with legitimate cell values
    reclass = arcpy.sa.Con(arcpy.sa.IsNull(str(in_file)), 1, str(in_file), 'Value = 1')
    arcpy.RasterToASCII_conversion(in_raster=reclass, out_ascii_file=str(out_file))


