# Creates soil texture map by merging gSSURGO and STATSGO2
# Script written in Python 2.7, not compatible with Python 3.X

import arcpy
from arcpy import env
import config as config
from pathlib import Path
import tempfile
import pandas as pd
import numpy as np
import imp
from soil_merger import mergeSoils
import errno
from utils import reshape, getDEMspecs, getROI

imp.reload(config)
arcpy.CheckOutExtension('Spatial')
# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

# =======================================================================
# Get soil texture classes
# =======================================================================

def create_texture_map(in_soil):
    arcpy.MakeRasterLayer_management(in_raster=in_soil, out_rasterlayer='soil_raster_layer', band_index="1")
    fields = [field.name for field in arcpy.ListFields('soil_raster_layer')]
    if 'texcl' not in [field.lower() for field in fields]:
        component = str(Path(in_soil).parents[0] / 'component')
        arcpy.JoinField_management(in_data='soil_raster_layer', in_field='MUKEY', join_table=component,
                                   join_field='mukey',
                                   fields='cokey')

        chorizon = str(Path(in_soil).parents[0] / 'chorizon')
        arcpy.MakeRasterLayer_management(in_raster=in_soil, out_rasterlayer='soil_raster_layer', band_index="1")
        soil_raster_layer = arcpy.JoinField_management(in_data='soil_raster_layer', in_field='cokey',
                                                       join_table=chorizon,
                                                       join_field='cokey', fields='chkey')

        chtexturegrp = str(Path(in_soil).parents[0] / 'chtexturegrp')
        arcpy.MakeRasterLayer_management(in_raster=in_soil, out_rasterlayer='soil_raster_layer', band_index="1")
        soil_raster_layer = arcpy.JoinField_management(in_data='soil_raster_layer', in_field='chkey',
                                                       join_table=chtexturegrp,
                                                       join_field='chkey', fields='chtgkey')

        chtexture = str(Path(in_soil).parents[0] / 'chtexture')
        arcpy.MakeRasterLayer_management(in_raster=in_soil, out_rasterlayer='soil_raster_layer', band_index="1")
        soil_raster_layer = arcpy.JoinField_management(in_data='soil_raster_layer', in_field='chtgkey',
                                                       join_table=chtexture,
                                                       join_field='chtgkey')



roi = str(config.study_area)
dem_in = str(config.dem)
dem_out = str(config.dem_out)
roi_layers = getROI(roi, dem_in, temp_dir)

arcpy.Clip_management(in_raster=dem_in, out_raster=dem_out, in_template_dataset=roi_layers.roi, nodata_value=-9999,
                      clipping_geometry=True)
dem_specs = getDEMspecs(dem_out)

# gSSURGO map
gssurgo = str(config.gssurgo)
create_texture_map(gssurgo)

# STATSGO2 map
statsgo2 = str(config.statsgo2)
create_texture_map(statsgo2)

# Merge soil texture subclasses into classes, assign integer IDs
fields = ['texcl']
soil_out = str(config.gssurgo)
arcpy.MakeRasterLayer_management(in_raster=soil_out, out_rasterlayer='soil_out', band_index="1")
cursor = arcpy.da.SearchCursor('soil_out', fields)
df1 = pd.DataFrame(data=np.unique([row[0] for row in cursor]), columns=['texture'])

fields = ['TEXCL']
soil_out = str(config.statsgo2)
arcpy.MakeRasterLayer_management(in_raster=soil_out, out_rasterlayer='soil_out', band_index="1")
cursor = arcpy.da.SearchCursor('soil_out', fields)
df2 = pd.DataFrame(data=np.unique([row[0] for row in cursor]), columns=['texture'])

unique_classes = pd.concat([df1['texture'], df2['texture']]).unique()
df = pd.DataFrame(data=unique_classes, columns=['texture'])

# Create soil texture ID map
subclasses = {('Loamy sand', 'Loamy coarse sand', 'Loamy fine sand', 'Loamy very fine sand'): 1,
              ('Sandy loam', 'Coarse sandy loam', 'Very fine sandy loam', 'Fine sandy loam'): 2,
              ('Sand', 'Fine sand', 'Sand', 'Very fine sand', 'Sand', 'Coarse sand'): 3,
              ('Silt', 'Silt loam'): 4}

subclass_map = {}
for k, v in subclasses.items():
    for key in k:
        subclass_map[key] = v

# subclass_map['None'] = 0
subclass_map['Sandy clay loam'] = 5
subclass_map['Clay loam'] = 6
subclass_map['Clay'] = 7
subclass_map['Loam'] = 8
subclass_map['Silty clay'] = 9
subclass_map['Silty clay loam'] = 10
subclass_map['Sandy clay'] = 11

# Remap
remap_values = zip(subclass_map.keys(), subclass_map.values())
remap_values = arcpy.sa.RemapValue(remap_values)

# gssurgo_temp = temp_dir + '/gssurgo.tif'
# arcpy.CopyRaster_management(in_raster=gssurgo, out_rasterdataset=gssurgo_temp)
# for field in arcpy.ListFields(gssurgo_temp):
#     print field.name

# soil_remap = arcpy.sa.Reclassify(in_raster=gssurgo_temp, reclass_field='texcl', remap=remap_values)  # This doesn't work but it should
# soil_remap = arcpy.sa.Reclassify(in_raster=statsgo2, reclass_field='TEXCL', remap=remap_values)

# The following inputs are layers or table views: "statsgo2_text"
# If the above works, was going to use soil_remap to reshape and convert to ASCII
# Instead have to reclassify in ArcMap to new files, then continue from there
# Manually add the file paths for gssurgo_reclass/statsgo_reclass below after creation in ArcMap
gssurgo_reclass = 'C:/Users/ipdavies/Documents/ArcGIS/Default.gdb/Reclass_Mapu2'
statsgo2_reclass = 'C:/Users/ipdavies/Documents/ArcGIS/Default.gdb/Reclass_Mapu3'

reshape(gssurgo_reclass, config.gssurgo_out, 'gSSURGO', 'NEAREST', dem_specs, temp_dir, roi_layers)
reshape(statsgo2_reclass, config.statsgo2_out, 'STATSGO2', 'NEAREST', dem_specs, temp_dir, roi_layers)

gssurgo_temp = temp_dir + '/gssurgo.asc'
statsgo2_temp = temp_dir + '/statsgo2.asc'

arcpy.RasterToASCII_conversion(in_raster=str(config.gssurgo_out), out_ascii_file=gssurgo_temp)
arcpy.RasterToASCII_conversion(in_raster=str(config.statsgo2_out), out_ascii_file=statsgo2_temp)

# Merge gSSURGO and STATSGO2 together
mergeSoils(gssurgo_temp, statsgo2_temp, str(config.soil_velma))