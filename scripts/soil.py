# Creates soil texture map by merging gSSURGO and STATSGO2
# Script written in Python 2.7, not compatible with Python 3.X

import __init__
import sys
import os
import arcpy
from arcpy import env
import config as config
from pathlib import Path
import tempfile
import imp
from soil_merger import mergeSoils
from utils import reshape, getDEMspecs, getROI

imp.reload(config)
arcpy.CheckOutExtension('Spatial')
# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()
temp_gdb = 'temp.gdb'
arcpy.CreateFileGDB_management(tmp_dir, temp_gdb)

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


# def create_depth_map(in_soil):
#     # Get soil classes and soil column depth
#     # =======================================================================
#     # Join raster to valu1 table in gSSURGO.gdb, get total soil depth (tk0_999a)
#     soil = str(config.soil_out)
#     arcpy.MakeRasterLayer_management(in_raster=soil, out_rasterlayer='soil_raster_layer', band_index="1")
#     valu1_table = str(Path(soil).parents[0] / 'Valu1')
#
#     arcpy.AddJoin_management(in_layer_or_view='soil_raster_layer', in_field='MUKEY', join_table=valu1_table, join_field='MUKEY')
#     fields = ['Valu1.MUKEY', 'Valu1.tk0_999a']
#     cursor = arcpy.da.SearchCursor('soil_raster_layer', fields)
#     df = pd.DataFrame(data=[row for row in cursor], columns=['MUKEY', 'tk0_999a_mm'])
#     df['tk0_999a_mm'] = df['tk0_999a_mm'].round(0) * 10
#     # Note: Some classes might have NaN values, what to do? Average them? They seem to be very small areas on land
#
#     # Get soil classes key
#     arcpy.MakeRasterLayer_management(in_raster=soil, out_rasterlayer='soil_raster_layer', band_index="1")
#     muaggatt_table = str(Path(soil).parents[0] / 'muaggatt')
#     arcpy.AddJoin_management(in_layer_or_view='soil_raster_layer', in_field='MUKEY', join_table=muaggatt_table, join_field='mukey')
#     fields = ['muaggatt.MUKEY', 'muaggatt.muname', 'muaggatt.hydgrpdcd', 'muaggatt.drclassdcd']
#     cursor = arcpy.da.SearchCursor('soil_raster_layer', fields)
#     df = pd.DataFrame(data=[row for row in cursor], columns=['MUKEY', 'Name', 'hydrologic_group', 'drainage_class_dom'])
#     soil_key = config.soil_velma.parents[0] / 'soil_class_key.csv'
#     df.to_csv(str(soil_key), index=False)

# # To view all fields
# for field in arcpy.ListFields('soil_raster_layer'):
#     print("{0} is a type of {1} with a length of {2}"
#           .format(field.name, field.type, field.length))



roi = str(config.study_area)
proj = str(config.proj_wkt)
cell_size = config.cell_size
dem_velma = str(config.dem_velma)
roi_layers = getROI(roi, tmp_dir, proj)

dem_specs = getDEMspecs(dem_velma)

# gSSURGO map
gssurgo = str(config.gssurgo)
create_texture_map(gssurgo)

# STATSGO2 map
statsgo2 = str(config.statsgo2)
create_texture_map(statsgo2)

# # Merge soil texture subclasses into classes, assign integer IDs
# fields = ['texcl']
# soil_out = str(config.gssurgo)
# arcpy.MakeRasterLayer_management(in_raster=soil_out, out_rasterlayer='soil_out', band_index="1")
# cursor = arcpy.da.SearchCursor('soil_out', fields)
# df1 = pd.DataFrame(data=np.unique([row[0] for row in cursor]), columns=['texture'])
#
# fields = ['TEXCL']
# soil_out = str(config.statsgo2)
# arcpy.MakeRasterLayer_management(in_raster=soil_out, out_rasterlayer='soil_out', band_index="1")
# cursor = arcpy.da.SearchCursor('soil_out', fields)
# df2 = pd.DataFrame(data=np.unique([row[0] for row in cursor]), columns=['texture'])
#
# unique_classes = pd.concat([df1['texture'], df2['texture']]).unique()
# df = pd.DataFrame(data=unique_classes, columns=['texture'])
#
# # Create soil texture ID map
# subclasses = {('Loamy sand', 'Loamy coarse sand', 'Loamy fine sand', 'Loamy very fine sand'): 1,
#               ('Sandy loam', 'Coarse sandy loam', 'Very fine sandy loam', 'Fine sandy loam'): 2,
#               ('Sand', 'Fine sand', 'Sand', 'Very fine sand', 'Sand', 'Coarse sand'): 3,
#               ('Silt', 'Silt loam'): 4}
#
# subclass_map = {}
# for k, v in subclasses.items():
#     for key in k:
#         subclass_map[key] = v
#
# # subclass_map['None'] = 0
# subclass_map['Sandy clay loam'] = 5
# subclass_map['Clay loam'] = 6
# subclass_map['Clay'] = 7
# subclass_map['Loam'] = 8
# subclass_map['Silty clay'] = 9
# subclass_map['Silty clay loam'] = 10
# subclass_map['Sandy clay'] = 11

# # # Remap
# remap_values = zip(subclass_map.keys(), subclass_map.values())
# remap_values = arcpy.sa.RemapValue(remap_values)
#
# # gssurgo_temp = tmp_dir + '/gssurgo.tif'
# arcpy.CopyRaster_management(in_raster=str(config.gssurgo_out), out_rasterdataset=gssurgo_temp)
# for field in arcpy.ListFields(gssurgo):
#     print field.type

# soil_remap = arcpy.sa.Reclassify(in_raster=gssurgo, reclass_field='texcl', remap=remap_values)  # This doesn't work but it should
# soil_remap = arcpy.sa.Reclassify(in_raster=statsgo2, reclass_field='TEXCL', remap=remap_values)

# This is a hacky solution - copied Python snippet from running reclassify in ArcMap
remap_values = "'Silt loam' 4;'Sandy loam' 2;'Fine sandy loam' 2;Loam 8;'Coarse sandy loam' 2;'Loamy sand' 1;Sand 3;'Loamy fine sand' 1;'Sandy clay loam' 5;'Very fine sandy loam' 2;'Coarse sand' 3;'Clay loam' 6;'Loamy coarse sand' 1;'Fine sand' 3;'Silty clay loam' 10;'Silty clay' 9;Clay 7;'Very fine sand' 3;Silt 4;'Loamy very fine sand' 1"
gssurgo_reclass = tmp_dir + '/temp.gdb/gssurgo_reclass'
arcpy.gp.Reclassify_sa(gssurgo, "texcl", remap_values, gssurgo_reclass, "DATA")

statsgo2_reclass = tmp_dir + '/temp.gdb/statsgo2_reclass'
arcpy.gp.Reclassify_sa(statsgo2, 'TEXCL', remap_values, statsgo2_reclass, "DATA")

gssurgo_tmp = tmp_dir + '/gssurgo.tif'
reshape(gssurgo_reclass, gssurgo_tmp, 'gSSURGO', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)
statsgo2_tmp = tmp_dir + '/statsgo2.tif'
reshape(statsgo2_reclass, statsgo2_tmp, 'STATSGO2', 'NEAREST', dem_specs, cell_size, proj, tmp_dir, roi_layers)


arcpy.Delete_management(gssurgo_reclass)
arcpy.Delete_management(statsgo2_reclass)
del gssurgo_reclass
del statsgo2_reclass

gssurgo_temp = tmp_dir + '/gssurgo.asc'
statsgo2_temp = tmp_dir + '/statsgo2.asc'

arcpy.RasterToASCII_conversion(in_raster=gssurgo_tmp, out_ascii_file=gssurgo_temp)
arcpy.RasterToASCII_conversion(in_raster=statsgo2_tmp, out_ascii_file=statsgo2_temp)

# Merge gSSURGO and STATSGO2 together
mergeSoils(gssurgo_temp, statsgo2_temp, str(config.soil_velma))

arcpy.Delete_management(str(config.soil_velma.parents[0] / '{}_mergedFile.asc'.format(config.soil_velma.stem)))
arcpy.Delete_management(gssurgo_temp)
arcpy.Delete_management(statsgo2_temp)


