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
imp.reload(config)

# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

# =======================================================================================
# Resample Ellsworth DEM from 1m to 10m, then mosaic with DEM data outside of study area
# =======================================================================================

# Would be more dynamic to open the study area and get extent from that, in case DEM isn't already clipped

dem_raw = str(config.dem_raw)
dem_resamp = temp_dir + '/dem_resamp.tif'

# Resample study area DEM
arcpy.Resample_management(in_raster=dem_raw, out_raster=dem_resamp, cell_size="10 10", resampling_type="CUBIC")

dem_border = str(config.dem_border)
dem_border_proj = temp_dir + '/dem_border_proj.tif'
dem_border_clip = temp_dir + '/dem_border_clip.tif'
dem = str(config.dem)  # Final output DEM

# Get cell size and minimum bounding box of study area DEM
x = arcpy.GetRasterProperties_management(dem_resamp, 'CELLSIZEX').getOutput(0)
y = arcpy.GetRasterProperties_management(dem_resamp, 'CELLSIZEY').getOutput(0)
xy = '{} {}'.format(x, y)
proj = arcpy.Describe(dem_resamp).spatialReference
extent = arcpy.sa.Raster(dem_resamp).extent
envelope = '{} {} {} {}'.format(extent.XMin, extent.YMin, extent.XMax, extent.YMax)

# Reproject, clip, and mosaic border DEM
arcpy.ProjectRaster_management(in_raster=dem_border, out_raster=dem_border_proj, out_coor_system=proj,
                               resampling_type='CUBIC',
                               cell_size=xy)

arcpy.Clip_management(in_raster=dem_border_proj, out_raster=dem_border_clip, rectangle=envelope, nodata_value=-9999)

arcpy.Mosaic_management([dem_resamp, dem_border_clip], target=dem_border_clip, mosaic_type='FIRST')

arcpy.RasterToASCII_conversion(in_raster=dem_border_clip, out_ascii_file=dem)

