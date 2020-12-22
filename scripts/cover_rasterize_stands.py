# Rasterizes stand shapefiles into separate rasters of age, type, and VELMA ID
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio import features
from utils import flowlines
from pathlib import Path
from soil_merger import readHeader
import tempfile
from scipy import ndimage
import importlib
importlib.reload(config)
# ======================================================================================================================

# =======================================================================
# Convert Ellsworth stand vector to raster
# =======================================================================

# Create temp directory for intermediary files
temp_dir = tempfile.mkdtemp()

filter_dir = config.cover_id_velma.parents[0] / 'filter_maps'

# Edit species names to be VELMA appropriate and fill nulls
stand_shp = str(config.stand_shp)
stand_shp = gpd.read_file(config.stand_shp)

# Replace slashes with underscores
stand_shp['STAND_TYPE'] = stand_shp['STAND_TYPE'].str.replace('/', '_')
stand_shp['STAND_TYPE'] = stand_shp['STAND_TYPE'].str.replace('-', '_')

# Fix some errors and combine duplicate stand types
stand_shp.loc[pd.isnull(stand_shp['STAND_TYPE']), 'STAND_TYPE'] = 'BARE'
stand_shp['STAND_TYPE'] = stand_shp['STAND_TYPE'].replace('TNC', 'DF')  # Changing these errors to DF
stand_shp['STAND_TYPE'] = stand_shp['STAND_TYPE'].replace('50074', 'DF')
stand_shp['STAND_TYPE'] = stand_shp['STAND_TYPE'].replace('WH_RC_SS_RA', 'WH_SS_RC_RA')

# Remove numeric suffixes
p = [[j for j in i if not j.isnumeric()] for i in stand_shp['STAND_TYPE'].str.split('_')]
p = ['_'.join(i) for i in p]
stand_shp['STAND_TYPE'] = p

# CHANGING THEM ALL TO CONIFER FOR EASE IN VELMA
conifers = stand_shp['STAND_TYPE'].unique().tolist()
conifers = [x for x in conifers if x not in ['BARE', 'BPA', 'NF']]
stand_shp['STAND_TYPE'] = stand_shp['STAND_TYPE'].replace(dict.fromkeys(conifers, 'conifer'))

# Assign numbers to unique species names
unique_species = stand_shp['STAND_TYPE'].unique().tolist()
unique_numbers = (np.arange(len(unique_species))+1).tolist()
species_num_dict = {unique_species[i]: unique_numbers[i] for i in range(len(unique_species))}
stand_shp['SPECIES_ID'] = stand_shp['STAND_TYPE'].map(species_num_dict)
key = pd.DataFrame(np.column_stack([unique_species, unique_numbers]), columns=['type', 'id'])  # Save species/number key
key.to_csv(config.cover_type_velma.parents[0] / 'cover_type_key.csv', index=False)

# Convert ages from strings to numbers
stand_shp['Age_2020'].replace('200+', '200', inplace=True)
stand_shp['Age_2020'] = stand_shp['Age_2020'].astype(int)
stand_shp.loc[pd.isnull(stand_shp['Age_2020']), 'Age_2020'] = 0

# Assign unique numbers to each stand+type combo (some stands have multiple stand types, so we can't use STAND_ID)
stand_shp.insert(0, 'VELMA_ID', range(1, len(stand_shp)+1))
# Export shp as csv for creating disturbance map based on stand IDs
stand_shp_csv = pd.DataFrame(stand_shp.drop(columns='geometry'))
stand_shp_csv.to_csv(config.cover_id_velma.parents[0] / 'disturbance_map.csv', index=False)

# Reproject to DEM crs
dem_file = str(config.dem_raw)
with rasterio.open(dem_file, 'r') as src:
    dem_crs = src.crs.to_string()
stand_shp = stand_shp.to_crs(dem_crs)
updated_shp = config.stand_shp.parents[0] / 'Ellsworth_Stands_updated.shp'
stand_shp.to_file(updated_shp)

# Convert vector to raster (stand type)
stand_type = str(config.cover_type)
# Take DEM and set all values to NaN, then burn species shp into empty DEM raster
with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = -9999
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(stand_type, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(stand_shp.geometry, stand_shp.SPECIES_ID))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)

# Convert vector to raster (stand age)
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

# Convert vector to raster (stand ID)
stand_id = str(config.cover_id)
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

# WA requires a 10 meter no-management buffer around all streams, so will add those in with ID=0
# Create flowlines raster and buffer it by 1 cell (10m/30ft)
flow = flowlines(config.flowlines)
flow.get_flowlines_ascii(temp_dir)
no_mgmt_buffer = ndimage.binary_dilation(flow.raster, iterations=1)

# Overlay buffer on cover ID map and export
cover_ids = np.loadtxt(str(config.cover_id_velma), skiprows=6)  # Each stand has a different number
cover_ids[no_mgmt_buffer] = 0

outfile = str(filter_dir / 'filtermap.asc')
header = readHeader(str(config.cover_id_velma))
f = open(outfile, "w")
f.write(header)
np.savetxt(f, cover_ids, fmt="%i")
f.close()


