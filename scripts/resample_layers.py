import arcpy
from arcpy import env
arcpy.CheckOutExtension('Spatial')
from arcpy.sa import Fill
import tempfile
import config as config
from pathlib import Path
import numpy as np
import imp
from utils import getROI
imp.reload(config)

# ======================================================================================================================
# Set environment settings
env.workspace = str(config.data_path)
arcpy.env.overwriteOutput = True

# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()

# =======================================================================================
velma_data = config.data_path / 'ellsworth_velma'

input_files = [velma_data / 'landcover' / 'cover_age.asc', velma_data / 'landcover' / 'cover_id.asc',
               velma_data / 'soil' / 'MapunitRaster_10m.asc', velma_data / 'landcover' / 'conifer.asc',
               velma_data / 'landcover' / 'permeability.asc']

input_rasters = [tmp_dir + '\\{}_raster.tif'.format(x.stem) for x in input_files]

resampled = [tmp_dir + '\\{}.tif'.format(x.stem) for x in input_files]

output_files = [Path(str(x).replace('ellsworth_velma', 'ellsworth_5m_velma')) for x in input_files]

proj = config.proj_wkt
for i, file in enumerate(input_files):
    arcpy.ASCIIToRaster_conversion(str(file), input_rasters[i], "FLOAT")
    arcpy.ProjectRaster_management(in_raster=input_rasters[i], out_raster=resampled[i], out_coor_system="PROJCS['NAD_1983_UTM_Zone_10N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-123.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
                                   in_coor_system="PROJCS['NAD_1983_UTM_Zone_10N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-123.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
                                   resampling_type='NEAREST', cell_size=config.cell_size)
    try:
        output_files[i].parents[0].mkdir(parents=True)
    except WindowsError:
        pass

    arcpy.RasterToASCII_conversion(in_raster=resampled[i], out_ascii_file=str(output_files[i]))



