# Resamples Ellsworth DEM from 1m to 10m and mosaics with border DEM outside of study area
# This is done because JPDEM/VELMA require rasters without NoData cells
# Note: Ellsworth DEM is already clipped to study area and it's extent is used to clip border DEM
# Script written in Python 2.7, not compatible with Python 3.X

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

# =======================================================================================
# Resample DEM to desired resolution, then mosaic with DEM data outside of study area to
# get a rectangular raster with no missing data
# =======================================================================================

input_dems = ['elevEllsworth_2019roads_on_2007dtm', 'els_dtm2019_fin', 'elevEllsworth_2007roads_on_2019dtm',
              'els_dtm2019_clip100ft', 'els_dtm_2007_fin', 'els_dtm2007_clip100ft']

dem_dir = config.data_path / 'topography' / 'ellsworth' / 'Ellsworth_Elevation_Products.gdb'
output_dir = config.data_path / 'topography' / 'ellsworth' / 'Ellsworth_Elevation_Products_5m_merged'

try:
    Path(output_dir).mkdir(parents=True)
except WindowsError:
    pass

# Get extent of study area
study_area = str(config.study_area)
proj = str(config.proj_wkt)
roi = getROI(study_area, tmp_dir, proj)
extent = arcpy.Describe(roi.roi).extent
envelope = '{} {} {} {}'.format(extent.XMin, extent.YMin, extent.XMax, extent.YMax)

for ds in input_dems:
    dem_raw = str(dem_dir / ds)
    dem = str(output_dir / '{}.asc'.format(ds))

    # Resample base DEM to desired projection and cell size
    dem_resamp = tmp_dir + '/dem_resamp.tif'
    arcpy.ProjectRaster_management(in_raster=dem_raw, out_raster=dem_resamp, out_coor_system=proj,
                                   resampling_type='CUBIC', cell_size=config.cell_size)

    # Clip base DEM to study area
    dem_resamp_clip = tmp_dir + '/dem_resamp_clip.tif'
    arcpy.Clip_management(in_raster=dem_resamp, out_raster=dem_resamp_clip, rectangle=envelope, nodata_value=-9999)

    # Reproject, clip, and mosaic border DEM
    dem_border = str(config.dem_border)
    dem_border_proj = tmp_dir + '/dem_border_proj.tif'
    arcpy.ProjectRaster_management(in_raster=dem_border, out_raster=dem_border_proj, out_coor_system=proj,
                                   resampling_type='CUBIC', cell_size=config.cell_size)

    # Mosaic base DEM with border DEM
    arcpy.Mosaic_management([dem_resamp_clip, dem_border_proj], target=dem_border_proj, mosaic_type='FIRST')
    # arcpy.management.Delete(dem_resamp_clip)

    # Clip mosaicked DEM
    dem_border_clip = tmp_dir + '/dem_border_clip.tif'
    arcpy.Clip_management(in_raster=dem_border_proj, out_raster=dem_border_clip, rectangle=envelope, nodata_value=-9999)

    # Export
    arcpy.RasterToASCII_conversion(in_raster=dem_border_clip, out_ascii_file=dem)
    # arcpy.management.Delete(dem_border_clip)



