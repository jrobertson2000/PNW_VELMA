# Resamples Ellsworth DEM from 1m to 10m
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
temp_gdb = 'temp.gdb'
arcpy.CreateFileGDB_management(temp_dir, temp_gdb)

# =======================================================================
# Resample Ellsworth DEM from 1m to 10m
# =======================================================================

dem_raw = str(config.dem_raw)
# dem_resamp = temp_dir + '/dem_resamp.tif'
dem = str(config.dem)

# Resample
arcpy.Resample_management(in_raster=dem_raw, out_raster=dem, cell_size="10 10", resampling_type="CUBIC")



