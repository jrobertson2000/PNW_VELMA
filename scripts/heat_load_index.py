# Calculate heat load index for study area
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
import config as config
import imp
imp.reload(config)
# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# =======================================================================
# Calculate heat load index for study area
# =======================================================================

dem_velma = str(config.dem_velma)
hli_out = str(config.hli_out)

# Calculate HLI
arcpy.ImportToolbox(str(config.geomorph_tbx_path))
arcpy.hli(Select_DEM=dem_velma, HLI_Output_Raster=hli_out)

# Convert to ASCII
hli_velma = str(config.hli_velma)
arcpy.RasterToASCII_conversion(in_raster=hli_out, out_ascii_file=hli_velma)

