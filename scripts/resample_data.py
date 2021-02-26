
import config as config
import os
import glob
import rasterio
from soil_merger import readHeader
from rasterio.enums import Resampling
from pathlib import Path
# ======================================================================================================================

orig_res = 10
new_res = 5
upscale_factor = orig_res / new_res

old_paths = [config.cover_age_velma, config.cover_id_velma, config.soil_velma,
             config.velma_data / 'landcover' / 'conifer.asc',
             config.velma_data / 'landcover' / 'permeability.asc']

new_paths = [Path(str(x).replace('ellsworth_velma', 'ellsworth_velma_5m')) for x in old_paths]

# Add the disturbance filter maps
filter_map_dir = config.velma_data / 'landcover' / 'filter_maps'
for file in os.listdir(str(filter_map_dir)):
    if file.endswith('.asc'):
        old_paths.append(filter_map_dir / file)


# Resample categorical data files to desired resolution
new_files = []
for file in old_paths:
    with rasterio.open(file, 'r') as ds:
        data = ds.read(out_shape=(ds.count,
                                  int(ds.height * upscale_factor),
                                  int(ds.width * upscale_factor)),
                       resampling=Resampling.nearest)
        new_files.append(data)

# Export resampled files
header = readHeader(old_paths[0])
#for file in new_files:
with rasterio.open(new_paths[0], 'w', 'AAIGrid') as dst:
    dst.write(new_files[0], 1)


# =======================================================================================
# Resample DEM files if necessary

orig_res_dem = 3
new_res_dem = 5
upscale_factor_dem = orig_res_dem / new_res_dem

old_dem_files = []

dem_dir = config.velma_data.parents[0] / 'ellsworth_3m_velma' / 'topography'
for file in os.listdir(str(dem_dir)):
    old_dem_files.append(dem_dir / file)

# Resample categorical data files to desired resolution
with rasterio.open(old_dem_files[0], 'r') as ds:
    data = ds.read(out_shape=(ds.count,
                              int(ds.height * upscale_factor_dem),
                              int(ds.width * upscale_factor_dem)),
                   resampling=Resampling.cubic)


# # Resample all files to desired resolution
# proj = arcpy.Describe(config.dem).spatialReference
# arcpy.ProjectRaster_management(in_raster=old_files[0], out_raster=new_files[0], out_coor_system=proj,
#                                resampling_type='CUBIC',
#                                cell_size=xy)

