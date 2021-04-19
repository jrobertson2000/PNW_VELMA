# Creates filter-maps for VELMA based on historical forest disturbances derived from Hansen Forest Loss dataset
# Additionally, estimates pre-Hansen disturbances using stand age map and working backwards
# Script written in Python 3.7

import config as config
import numpy as np
from soil_merger import readHeader
import importlib

importlib.reload(config)
# ======================================================================================================================

# Calculated from UMD Hansen Global Forest Change
# Raster where pixel values are year of forest loss
# https://code.earthengine.google.com/abedd30c322f12650b6304b597273e9a
yearly_loss_path = config.yearly_forest_loss_velma

filter_dir = config.stand_id_velma.parents[0] / 'filter_maps'
try:
    filter_dir.mkdir(parents=True)
except FileExistsError:
    pass

hansen_yearly_loss = np.loadtxt(yearly_loss_path, skiprows=6)

hansen_years = np.unique(hansen_yearly_loss).tolist()
hansen_years.remove(0)

# =======================================================================
# Combine the Hansen forest loss maps with pre-2000 (pre-Hansen) disturbances estimated based on stand age data

start = 1984
end = 2021
age_diff = end - start

cover_age = np.loadtxt(config.cover_age_velma, skiprows=6)
age_count = cover_age - age_diff

# Subtract age difference between start and end period from current age raster.
# Age+1 each year, and cells are cut down when cells=0
prehansen_cuts = []
prehansen_years = []
for year in range(start, end):
    loss_map = (age_count == 0)
    prehansen_cuts.append(loss_map)
    prehansen_years.append(year)
    age_count += 1

# Export historical clearcut filter maps
header = readHeader(config.cover_age_velma)

for i, year in enumerate(range(start, end)):
    prehansen_loss = prehansen_cuts[prehansen_years.index(year)]
    hansen_loss = (hansen_yearly_loss == year % 100) * 1
    total_loss = hansen_loss + prehansen_loss
    if total_loss.sum() > 0:
        print(year)
        outfile = filter_dir / 'historical_clearcut_{}.asc'.format(year)
    f = open(outfile, "w")
    f.write(header)
    np.savetxt(f, total_loss, fmt="%i")
    f.close()









