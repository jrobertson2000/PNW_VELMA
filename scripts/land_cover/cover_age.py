# This script takes the current cover age map and adjusts it to include any disturbances found in the
# Hansen Forest Loss dataset. The exported cover age map correponds to the desired VELMA simulation start date
# Script written in Python 3.7

import config as config
import numpy as np
from soil_merger import readHeader
import importlib
# ======================================================================================================================

# Date of current cover age map
current_map_date = 2020

# Date of VELMA simulation start
sim_start = 2020

# Map of Hansen forest loss disturbances. Value = year of disturbance
yearly_loss_path = config.yearly_forest_loss_velma
yearly_loss = np.loadtxt(yearly_loss_path, skiprows=6)
years = np.unique(yearly_loss)

# Remove disturbances that occur after simulation start date, because they won't have occurred yet
yearly_loss_sim = yearly_loss.copy()
yearly_loss_sim[yearly_loss_sim >= sim_start % 100] = 0
losses_occurred = (yearly_loss_sim != 0)

# Override current cover age map with Hansen loss map, only where losses occurred before simulation start date
current_cover_age_path = config.cover_age_velma
current_cover_age = np.loadtxt(current_cover_age_path, skiprows=6)
cover_age_updated = current_cover_age.copy()
elapsed_time = current_map_date % 100 - losses_occurred
cover_age_updated[losses_occurred] = elapsed_time[losses_occurred]

# Bring updated age map to desired simulation start date
historical_cover_age_sim = cover_age_updated + (sim_start % 100 - current_map_date % 100)

# Export updated, historical cover age map for the simulation start date
header = readHeader(config.cover_age_velma)
outfile = config.cover_age_velma.parents[0] / 'historical_age_{}.asc'.format(sim_start)
f = open(outfile, 'w')
f.write(header)
np.savetxt(f, historical_cover_age_sim, fmt='%i')
f.close()