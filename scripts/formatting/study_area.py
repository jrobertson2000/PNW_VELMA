# Create binary mask of study area for VELMA delineation and allows user to identify outpour point graphically
# Script written in Python 3.7

import config as config
import numpy as np
import geopandas as gpd
import rasterio
import tempfile
from rasterio import features
from soil.soil_merger import readHeader
from scipy.ndimage.morphology import binary_fill_holes
import importlib
importlib.reload(config)
# ======================================================================================================================

tmp_dir = tempfile.mkdtemp()

# =======================================================================
# Rasterize study area and convert to binary mask
# =======================================================================
roi = gpd.read_file(config.study_area)
cols = roi.columns.to_list()
cols.remove('geometry')
roi = roi.drop(cols, axis=1)
roi['value'] = 1

dem_file = str(config.dem_velma)

roi_raster = config.dem_velma.parents[1] / 'roi.asc'

# Take DEM and set all values to NaN, then burn species shp into empty DEM raster
with rasterio.open(dem_file, 'r') as src:
    in_arr = src.read(1)
    in_arr[:] = 0
    meta = src.meta.copy()
    meta = src.meta
    with rasterio.open(roi_raster, 'w+', **meta) as out:
        shapes = ((geom, value) for geom, value in zip(roi.geometry, roi.value))
        burned = features.rasterize(shapes=shapes, fill=np.nan, out=in_arr, transform=out.transform)
        out.write_band(1, burned)

roi_header = readHeader(roi_raster)
roi_asc = np.loadtxt(roi_raster, skiprows=6)


# =======================================================================
# Vectorize delineated DEM (area upstream of outpour point, as exported from JPDEM)
# =======================================================================

dem_path = config.dem_velma.parents[0] / 'delineated_dem.asc'
dem = np.loadtxt(dem_path, skiprows=6)

dem_simple = dem.astype('int16')
dem_simple[dem_simple > 1] = 1
dem_simple[dem_simple < 1] = 0
dem_simple = binary_fill_holes(dem_simple).astype(int)

outfile = tmp_dir + '/upstream.asc'
header = readHeader(str(dem_path))
f = open(outfile, "w")
f.write(header)
np.savetxt(f, dem_simple, fmt="%i")
f.close()

with rasterio.Env():
    with rasterio.open(outfile) as src:
        image = src.read()
        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v)
            in enumerate(rasterio.features.shapes(image, transform=src.transform)))

geoms = list(results)

upstream = gpd.GeoDataFrame.from_features(geoms)
upstream = upstream[upstream.raster_val != 0]
crs = roi.crs
upstream = upstream.set_crs(roi.crs)
upstream.to_file('upstream_ells_mouth.shp')






