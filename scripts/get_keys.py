# Get keys for cover maps
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
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
# Get soil classes and soil column depth
# =======================================================================
# Join raster to valu1 table in gSSURGO.gdb, get total soil depth (tk0_999a)
soil = str(config.soil_out)
arcpy.MakeRasterLayer_management(in_raster=soil, out_rasterlayer='soil_raster_layer', band_index="1")
valu1_table = str(Path(soil).parents[0] / 'Valu1')

arcpy.AddJoin_management(in_layer_or_view='soil_raster_layer', in_field='MUKEY', join_table=valu1_table, join_field='MUKEY')
fields = ['Valu1.MUKEY', 'Valu1.tk0_999a']
cursor = arcpy.da.SearchCursor('soil_raster_layer', fields)
df = pd.DataFrame(data=[row for row in cursor], columns=['MUKEY', 'tk0_999a_mm'])
df['tk0_999a_mm'] = df['tk0_999a_mm'].round(0) * 10
# Note: Some classes might have NaN values, what to do? Average them? They seem to be very small areas on land

# Get soil classes key
arcpy.MakeRasterLayer_management(in_raster=soil, out_rasterlayer='soil_raster_layer', band_index="1")
muaggatt_table = str(Path(soil).parents[0] / 'muaggatt')
arcpy.AddJoin_management(in_layer_or_view='soil_raster_layer', in_field='MUKEY', join_table=muaggatt_table, join_field='mukey')
fields = ['muaggatt.MUKEY', 'muaggatt.muname', 'muaggatt.hydgrpdcd', 'muaggatt.drclassdcd']
cursor = arcpy.da.SearchCursor('soil_raster_layer', fields)
df = pd.DataFrame(data=[row for row in cursor], columns=['MUKEY', 'Name', 'hydrologic_group', 'drainage_class_dom'])
soil_key = config.soil_velma.parents[0] / 'soil_class_key.csv'
df.to_csv(str(soil_key), index=False)

# # To view all fields
# for field in arcpy.ListFields('soil_raster_layer'):
#     print("{0} is a type of {1} with a length of {2}"
#           .format(field.name, field.type, field.length))

# =======================================================================
# Get landcover classes
# =======================================================================
nlcd = str(config.nlcd_out)
arcpy.MakeRasterLayer_management(in_raster=nlcd, out_rasterlayer='nlcd_raster_layer', band_index="1")
fields = ['Value']
cursor = arcpy.da.SearchCursor('nlcd_raster_layer', fields)
df = pd.DataFrame(data=[row for row in cursor], columns=['Value'])
df['tk0_999a_mm'] = df['tk0_999a_mm'].round(0) * 10

# Create cover species name/ID table from the classes present in raster
key_file = Path(nlcd).parents[0] / 'nlcd_key.csv'
key = pd.read_csv(str(key_file))
key.drop('NLCD_Land', inplace=True, axis=1)
id_table = df.merge(key, on='Value', how='left')
output_file = str(config.nlcd_velma.parents[0] / 'cover_species_key.csv')
id_table.to_csv(output_file, index=False)



