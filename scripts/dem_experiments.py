# Script for formatting multiple DEMs with experimental road decommissioning
# Mosaics DEMS with border DEM outside of study area
# This is done because JPDEM/VELMA require rasters without NoData cells
# Note: Ellsworth DEM is already clipped to study area and it's extent is used to clip border DEM
# Script written in Python 2.7, not compatible with Python 3

import arcpy
from arcpy import env
arcpy.CheckOutExtension('Spatial')
from arcpy.sa import Fill
import tempfile
import config as config
from pathlib import Path
import numpy as np
import imp
from utils import getROI
imp.reload(config)

# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()
print('Temp dir:', tmp_dir)

# =======================================================================================
# Resample DEM to desired resolution, then mosaic with DEM data outside of study area to
# get a rectangular raster with no missing data
# =======================================================================================

arcpy.env.workspace = r'C:\\Users\\ipdavies\\tnc_velma\\data\\topography\\ellsworth\\Ellsworth_Elevation_Products.gdb'

dem_gdb = config.data_path / 'topography' / 'ellsworth' / 'Ellsworth_Elevation_Products.gdb'

dems_raw = ['els_dtm_2007_fin', 'els_dtm2019_fin', 'els_dtm2007_clip100ft', 'els_dtm2019_clip100ft',
            'elevEllsworth_2019roads_on_2007dtm', 'elevEllsworth_2007roads_on_2019dtm']
dems_raw = ['els_dtm2019_fin', 'els_dtm2007_clip100ft', 'els_dtm2019_clip100ft',
            'elevEllsworth_2019roads_on_2007dtm', 'elevEllsworth_2007roads_on_2019dtm']

for i, dem_path in enumerate(dems_raw):
    print(dem_path)
    dem_raw = str(dem_gdb / dem_path)
    out_dir = dem_gdb.parents[0] / 'Ellsworth_Elevation_Products_merged'
    try:
        out_dir.mkdir(parents=True)
    except WindowsError:
        pass
    dem_out = str(out_dir / '{}'.format(dem_path + '_merge.asc'))

    # Get cell size of DEM and reproject
    dem_ells = "C:/Users/ipdavies/tnc_velma/data/topography/ellsworth/dem_ells.tif"
    dem_raw_reproj = tmp_dir + '/dem_raw_reproj.tif'
    x = arcpy.GetRasterProperties_management(dem_raw, 'CELLSIZEX').getOutput(0)
    y = arcpy.GetRasterProperties_management(dem_raw, 'CELLSIZEY').getOutput(0)
    xy = '{} {}'.format(x, y)
    proj = arcpy.Describe(dem_ells).spatialReference

    arcpy.ProjectRaster_management(in_raster=dem_raw, out_raster=dem_raw_reproj, out_coor_system=proj,
                                   resampling_type='CUBIC',
                                   cell_size=xy)

    # Get extent of study area
    study_area = str(config.study_area)
    roi = getROI(study_area, dem_raw_reproj, tmp_dir)
    extent = arcpy.Describe(roi.roi).extent
    envelope = '{} {} {} {}'.format(extent.XMin, extent.YMin, extent.XMax, extent.YMax)
    extent_buff = arcpy.Describe(roi.roi_buff).extent
    envelope_buff = '{} {} {} {}'.format(extent_buff.XMin, extent_buff.YMin, extent_buff.XMax, extent_buff.YMax)

    dem_border = str(config.dem_border)
    dem_border_proj = tmp_dir + '/dem_border_proj.tif'
    dem_border_clip = tmp_dir + '/dem_border_clip.tif'
    dem_border_mosaic = tmp_dir + '/dem_border_mosaic.tif'
    dem_border_out = tmp_dir + '/dem_border_out.tif'

    # Clip high-res DEM to study area
    dem_raw_clip = tmp_dir + '/dem_raw_clip.tif'
    arcpy.Clip_management(in_raster=dem_raw_reproj, out_raster=dem_raw_clip, rectangle=envelope, nodata_value=-9999)

    # Clip, reproject, and mosaic border DEM

    # Project border DEM to correct projection
    arcpy.ProjectRaster_management(in_raster=dem_border, out_raster=dem_border_proj, out_coor_system=proj,
                                   resampling_type='CUBIC')

    # Clip border DEM to manageable size
    arcpy.Clip_management(in_raster=dem_border_proj, out_raster=dem_border_clip, rectangle=envelope_buff, nodata_value=-9999)

    # Resample border DEM
    arcpy.ProjectRaster_management(in_raster=dem_border_clip, out_raster=dem_border_mosaic, out_coor_system=proj,
                                   resampling_type='CUBIC', cell_size=xy)

    # Mosaic border and high-res DEM
    arcpy.Mosaic_management([dem_raw_clip, dem_border_mosaic], target=dem_border_mosaic, mosaic_type='FIRST')

    # Final clip to study area
    arcpy.Clip_management(in_raster=dem_border_mosaic, out_raster=dem_border_out, rectangle=envelope, nodata_value=-9999)

    # Export to ASCII
    arcpy.RasterToASCII_conversion(in_raster=dem_border_out, out_ascii_file=dem_out)



