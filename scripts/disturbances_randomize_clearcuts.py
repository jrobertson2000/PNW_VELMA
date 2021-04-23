# This script creates disturbance filter maps of randomly sampled stands for yearly clearcutting
# These random, staggered harvests are more realistic than clearcutting all eligible stands during the first sim year
# Script written in Python 3.7

import pandas as pd
import numpy as np
import config as config
import tempfile
from scipy import ndimage
from utils import flowlines
import geopandas as gpd
from soil_merger import readHeader
import rasterio
from rasterio import features
# ======================================================================================================================
# Import files to create protected areas

# Create temp directory for intermediary files
tmp_dir = tempfile.mkdtemp()

# WA requires a 10 meter no-management buffer around all streams, so will add those in with ID=0
# Create flowlines raster and buffer it by 1 cell (10m/30ft)
flow = flowlines(config.flowlines)
flow.get_flowlines_ascii(tmp_dir)
no_mgmt_buffer = ndimage.binary_dilation(flow.raster, iterations=1)

# Overlay buffer on stand ID map
stand_id_path = str(config.stand_id_velma)
stand_id = np.loadtxt(stand_id_path, skiprows=6)  # Each stand has a different number
stand_id[stand_id == -9999] = np.nan
stand_id[no_mgmt_buffer] = 0

# Import map of the Ellsworth Experimental Basins. Passive=0, Control=1, Active=2
exp_basins = np.loadtxt(config.exp_basins_velma, skiprows=6)
exp_basins[exp_basins == -9999] = np.nan

# Marbled murrelet habitat is a protected area that can't be harvested
murrelet_path = config.data_path / 'landcover' / 'murrelet_no_harvest.asc'
murrelet = np.loadtxt(murrelet_path, skiprows=6)
murrelet[murrelet == -9999] = np.nan

# =======================================================================
# Create (binary) disturbance filter maps for each forest management scenario

# Don't want industrial clearcuts to all happen on the first harvest day, so will stagger them randomly
start_date = 2020
end_date = 2099
yearly_cut = 0.1  # We want to clearcut 10% max of stands each year
clearcut_age = 35

# Import stand shapefile
stand_shp = gpd.read_file(config.stand_shp.parents[0] / 'Ellsworth_Stands_updated.shp')

# Randomly sample X% of eligible stands each year for clearcutting until all eligible stands are cut
# For the rest of the VELMA simulation, stands will be cut whenever they become eligible
stands = stand_shp.copy()
yearly_samples = []
for year in range(start_date, end_date):
    eligible = stands[stands['Age_2020'] >= clearcut_age]
    if len(eligible) == 0:
        break
    cut_number = int(np.ceil(len(stands) * yearly_cut))  # Number of stands to be harvested this year
    to_harvest = np.min([cut_number, len(eligible)])  # If cut_number > # of eligible stands, cut all remaining stands
    sample = eligible.sample(to_harvest)
    yearly_samples.append(sample)
    stands['Age_2020'] += 1
    stands.loc[stands['VELMA_ID'].isin(sample['VELMA_ID']), 'Age_2020'] = 0  # Set age of harvested stands to 0


# Rasterize harvest samples
dem_file = config.dem_velma
yearly_clearcuts = []
for stand in yearly_samples:
    with rasterio.open(dem_file, 'r') as src:
        template = src.read(1)
        template[:] = 0
        meta = src.meta.copy()
        shapes = stand.geometry
        harvest = features.rasterize(shapes=shapes, fill=0, out_shape=(src.height, src.width), out=template,
                                    transform=src.transform, default_value=1)

    protected = ((stand_id == 0) + (murrelet == 1))
    harvest[protected.astype('bool')] = 0
    if np.sum(harvest) > 0:
        yearly_clearcuts.append(harvest)


# Export clearcut harvests
filter_dir = config.stand_id_velma.parents[0] / 'filter_maps'
try:
    filter_dir.mkdir(parents=True)
except FileExistsError:
    pass
header = readHeader(dem_file)
for i, harvest in enumerate(yearly_clearcuts):
    outfile = filter_dir / 'random_35yr_clearcut_10pct_{}.asc'.format(i+1)
    f = open(outfile, "w")
    f.write(header)
    np.savetxt(f, harvest, fmt="%i")
    f.close()

# # To check sizes of each yearly harvest
# areas = []
# for cut in yearly_clearcuts:
#     area_sqm = np.sum(cut) * 100
#     area_sqkm = area_sqm * 1e-6
#     areas.append(area_sqkm)
# pd.DataFrame(areas, columns=['data']).describe()



