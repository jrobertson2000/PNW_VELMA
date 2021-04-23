# Rasterizes stand shapefiles into separate rasters of age, type, and VELMA ID
# Script written in Python 3.7

import config as config
import numpy as np
import geopandas as gpd
import rasterio
from rasterio import features
# ======================================================================================================================
# Import stand shapefile
stand_shp = gpd.read_file(config.stand_shp.parents[0] / 'Ellsworth_Stands_updated.shp')

# Import projection .wkt file used for all spatial files
proj = open(config.proj_wkt, 'r').read()

# Rasterize stand type
stand_type = str(config.cover_type)
# Take DEM and set all values to NaN, then burn species shp into empty DEM raster
dem_file = config.dem_velma
with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = -9999
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(stand_type, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(stand_shp.geometry, stand_shp.SPECIES_ID))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)
        out.crs = proj

# Rasterize stand age
stand_age = str(config.cover_age)
# Take DEM and set all values to NaN, then burn species shp into empty DEM raster
with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = -9999
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(stand_age, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(stand_shp.geometry, stand_shp.Age_2020))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)
        out.crs = proj

# Rasterize stand id
stand_id = str(config.stand_id_velma)
# Take DEM and set all values to NaN, then burn species shp into empty DEM raster
with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = -9999
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(stand_id, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(stand_shp.geometry, stand_shp.VELMA_ID))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)
        out.crs = proj

# =======================================================================
# Rasterize experimental basins

exp_basins = gpd.read_file(config.exp_basins)
treatment_map = {'Passive': 0,
                 'Control': 1,
                 'Active': 2}
exp_basins = exp_basins.replace({'TREATMENT': treatment_map})

with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = -9999
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(config.exp_basins_velma, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(exp_basins.geometry, exp_basins.TREATMENT))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)
        out.crs = proj
