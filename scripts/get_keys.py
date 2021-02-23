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
from soil_merger import mergeSoils
imp.reload(config)

# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()
temp_gdb = 'temp.gdb'
arcpy.CreateFileGDB_management(tmp_dir, temp_gdb)

# =======================================================================
# Soil
# =======================================================================
# Merge gSSURGO and STATSGO2 ascii files

gssurgo = str(config.gssurgo_out)
gssurgo_temp = tmp_dir + '/gssurgo.asc'

statsgo2 = str(config.statsgo2_out)
statsgo2_temp = tmp_dir + '/statsgo2.asc'

# Merge soil texture subclasses into classes, assign integer IDs
fields = ['texcl']
cursor = arcpy.da.SearchCursor('soil_raster_layer', fields)
df = pd.DataFrame(data=[row[0] for row in cursor], columns=['texture'])


arcpy.RasterToASCII_conversion(in_raster='texture', out_ascii_file=gssurgo_temp)


arcpy.RasterToASCII_conversion(in_raster=statsgo2, out_ascii_file=statsgo2_temp)

mergeSoils(gssurgo_temp, statsgo2_temp, str(config.soil_velma))


# Merge soil texture subclasses into classes, assign integer IDs
soil = str(config.soil_out)
arcpy.MakeRasterLayer_management(in_raster=soil, out_rasterlayer='soil_raster_layer', band_index="1")
fields = ['texcl']
cursor = arcpy.da.SearchCursor('soil_raster_layer', fields)
df = pd.DataFrame(data=[row[0] for row in cursor], columns=['texture'])

subclass_map = {'Loamy coarse sand': 'Loamy sand',
                'Loamy fine sand': 'Loamy sand',
                'Loamy very fine sand': 'Loamy sand',
                'Coarse sandy loam': 'Sandy loam',
                'Very fine sandy loam': 'Sandy loam',
                'Fine sandy loam': 'Sandy loam',
                'Fine sand': 'Sand',
                'Very fine sand': 'Sand',
                'Coarse sand': 'Sand',
                'Silt': 'Silt loam'}

df = pd.DataFrame(data=df['texture'].map(subclass_map).fillna(df['texture']), columns=['texture'])
df_unique = df['texture'].unique()
texture_keys = pd.DataFrame(data=np.column_stack([df_unique, np.arange(len(df_unique))+1]), columns=['texture', 'id'], dtype=['string', 'int64'])
texture_keys['id'][texture_keys['texture'].isnull()] = -9999

texture_keys_file = config.soil_velma.parents[0] / 'soil_class_key.csv'
texture_keys.to_csv(str(texture_keys_file), index=False)

# Remap
remap_values = zip(texture_keys['texture'], texture_keys['id'].astype('int'))
remap_values = arcpy.sa.RemapValue(remap_values)
remap_values = arcpy.sa.RemapValue([['Silt loam', 1], ['Sandy loam', 2], ['Loam', 3], [None, -9999], ['Loamy sand', 5], ['Sand', 6], ['Sandy clay loam', 7], ['Clay loam', 8], ['Silty clay loam', 9], ['Silty clay', 10], ['Clay', 11]])
soil_remap = arcpy.sa.Reclassify(in_raster=texture_raster, reclass_field='chtexture.texcl', remap=remap_values)
soil_remap = arcpy.sa.Reclassify(soil, 'texcl', remap_values, "")

# Save remapped texture raster
texture_raster = arcpy.sa.Lookup('soil_raster_layer', 'chtexture.texcl')

arcpy.CopyRaster_management('soil_raster_layer', str(config.soil), pixel_type='16_BIT_SIGNED', )
texture_out.save(str(config.soil))

soil = str(config.soil_out)
arcpy.MakeRasterLayer_management(in_raster=soil, out_rasterlayer='soil_raster_layer', band_index="1")
valu1_table = str(Path(soil).parents[0] / 'Valu1')

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



