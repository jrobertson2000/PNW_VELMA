from __future__ import print_function
import sys
# ======================================================================================================================

# =======================================================================
# PYTHON 2.X utilities
# =======================================================================
if sys.version_info[0] < 3:
    import arcpy
    from arcpy import env
    import tempfile
    import config as config
    import numpy as np
    import imp

    imp.reload(config)
    arcpy.CheckOutExtension('Spatial')

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
        print('Prepping ' + name + ' ...')
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
        print('Done')


    def velma_format(in_file, out_file):
        # Replace NoData values with legitimate cell values
        reclass = arcpy.sa.Con(arcpy.sa.IsNull(str(in_file)), 1, str(in_file), 'Value = 1')
        arcpy.RasterToASCII_conversion(in_raster=reclass, out_ascii_file=str(out_file))

# =======================================================================
# PYTHON 3.X utilities
# =======================================================================

if sys.version_info[0] >= 3:
    import geopandas as gpd
    import tempfile
    import rasterio
    from rasterio import features
    from soil_merger import readHeader
    import config as config
    import numpy as np

    class flowlines:
        """ Creates temporary ASCII file of flowlines from shapefile """

        def __init__(self, flow_path):
            self.shp = gpd.read_file(flow_path)
            self.raster_path = None
            self.raster_header = None
            self.raster = None

        def get_flowlines_ascii(self, temp_dir):
            cols = self.shp.columns.to_list()
            cols.remove('geometry')
            flow = self.shp.drop(cols, axis=1)
            flow['value'] = 1
            self.raster_path = temp_dir + '/flow_raster.asc'

            dem_file = str(config.dem_velma)

            with rasterio.open(dem_file, 'r') as src:
                in_arr = src.read(1)
                in_arr[:] = 0
                meta = src.meta.copy()
                meta = src.meta
                with rasterio.open(self.raster_path, 'w+', **meta) as out:
                    shapes = ((geom, value) for geom, value in zip(flow.geometry, flow.value))
                    burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
                    out.write_band(1, burned)

            self.raster_header = readHeader(self.raster_path)
            self.raster = np.loadtxt(self.raster_path, skiprows=6)


