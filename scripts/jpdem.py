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
from soil_merger import readHeader

# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

# =======================================================================
# Convert NoData to 0 and create a border mask for JPDEM flat-processing
# =======================================================================

dem_out = str(config.dem)
dem_jpdem_in = str(config.dem_out.parents[0] / 'dem_jpdem_in.asc')
dem_jpdem_border = str(config.dem_out.parents[0] / 'dem_jpdem_border.asc')
arcpy.RasterToASCII_conversion(in_raster=dem_out, out_ascii_file=dem_jpdem_in)

dem = np.loadtxt(dem_jpdem_in, skiprows=6)
header = readHeader(dem_jpdem_in)

# Create border/mask file of NoData cells
border = np.ones(dem.shape)
border[dem == -9999] = 0
f = open(dem_jpdem_border, "w")
f.write(header)
np.savetxt(f, border, fmt="%i")
f.close()

# Convert NoData cells in DEM to 0
dem[dem == -9999] = 0
f = open(dem_jpdem_in, "w")
f.write(header)
np.savetxt(f, dem, fmt="%i")
f.close()






