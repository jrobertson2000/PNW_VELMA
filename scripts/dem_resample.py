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

dem_in = str(config.data_path / 'topography' / 'ellsworth' / 'Surfaces_byTNC_v2007' / 'be_ellsworth_dem.tif')
dem_resamp = temp_dir + '/dem_resamp.tif'
dem_out = str(Path(dem_in).parents[0] / 'be_ellsworth_dem_filled_10m.tif')

# Resample
arcpy.Resample_management(in_raster=dem_in, out_raster=dem_resamp, cell_size="10 10", resampling_type="CUBIC")

# Fill sinks
dem_filled = Fill(dem_resamp)
dem_filled.save(dem_out)



