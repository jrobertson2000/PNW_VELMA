# Formats input data for VELMA ingestion
# Script written in Python 2.7, not compatible with Python 3.X

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
# Convert rasters to ascii
# =======================================================================

input_files = [config.dem_out, config.fac_out, config.nlcd_out, config.biomass_out, config.imperv_out,
               config.soil_out, config.prism_temp_out, config.prism_precip_out, config.hli_out]

output_files = [config.dem_velma, config.fac_velma, config.nlcd_velma, config.biomass_velma, config.imperv_velma,
                config.soil_velma, config.prism_temp_velma, config.prism_precip_velma, config.hli_velma]


for i in range(len(input_files)):
    print 'Converting ' + input_files[i].stem + ' to ASCII'
    try:
        output_files[i].parents[0].mkdir(parents=True)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
    arcpy.RasterToASCII_conversion(in_raster=str(input_files[i]), out_ascii_file=str(output_files[i]))

# Check that all rasters are the same dimensions as DEM, if not give warning


# =======================================================================
# Merge soil classes by major soil texture
# =======================================================================
# Soil key already has major soil textures for each MUKEY
soil_key = config.soil_velma.parents[0] / 'soil_class_key_with_chars.csv'
soil_key = pd.read_csv(str(soil_key))
remap_values = zip(soil_key['MUKEY'], soil_key['texture_key'])
soil_velma = str(config.soil_velma)

# Remap
remap_values = arcpy.sa.RemapValue(remap_values)
soil_remap = arcpy.sa.Reclassify(in_raster=soil_velma, reclass_field='Value', remap=remap_values)

# Rewrite soil_velma with remapped values
arcpy.RasterToASCII_conversion(in_raster=soil_remap, out_ascii_file=soil_velma)
arcpy.Delete_management(soil_remap)

# =======================================================================
# Create VELMA configuration file
# =======================================================================

# velma_config = pd.read_csv(config.data_path / )



