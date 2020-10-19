# Creates disturbance maps for harvest scenarios
# Script written in Python 2.7 for ArcPy, not compatible with Python 3.X

import arcpy
from arcpy import env
arcpy.CheckOutExtension('Spatial')
import config as config
from pathlib import Path
import tempfile
import pandas as pd
import numpy as np
import imp
import errno
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
# Create disturbance maps from stand rasters
# =======================================================================
# Requires disturbance_map.csv which must have columns VELMA_ID and DISTURBANCE=0 or 1

# Do disturbance stuff here

# Create binary disturbance map
dist_key_file = config.stand_id_velma.parents[0] / 'disturbance_map.csv'
dist_key = pd.read_csv(str(dist_key_file))
remap_values = zip(dist_key['VELMA_ID'], dist_key['DISTURBANCE'])
stand_id_out = str(config.stand_id_out)
dist_velma = str(config.dist_velma)

# Remap
remap_values = arcpy.sa.RemapValue(remap_values)
dist_map = arcpy.sa.Reclassify(in_raster=stand_id_out, reclass_field='Value', remap=remap_values)

# Convert disturbance map to ASCII format
arcpy.RasterToASCII_conversion(in_raster=dist_map, out_ascii_file=dist_velma)
arcpy.Delete_management(dist_map)



