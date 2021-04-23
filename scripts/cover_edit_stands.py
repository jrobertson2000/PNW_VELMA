# Edits features of the Ellsworth stand shapefile in preparation for rasterization
# Script written in Python 3.7

import config as config
import numpy as np
import pandas as pd
import geopandas as gpd
# ======================================================================================================================
# Edit stand shapefile

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
unique_numbers = (np.arange(len(unique_species)) + 1).tolist()
species_num_dict = {unique_species[i]: unique_numbers[i] for i in range(len(unique_species))}
stand_shp['SPECIES_ID'] = stand_shp['STAND_TYPE'].map(species_num_dict)
key = pd.DataFrame(np.column_stack([unique_species, unique_numbers]), columns=['type', 'id'])  # Save species/number key
key.to_csv(config.cover_type_velma.parents[0] / 'cover_type_key.csv', index=False)

# Convert ages from strings to numbers
stand_shp['Age_2020'].replace('200+', '200', inplace=True)
stand_shp['Age_2020'] = stand_shp['Age_2020'].astype(int)
stand_shp.loc[pd.isnull(stand_shp['Age_2020']), 'Age_2020'] = 0

# Assign unique numbers to each stand+type combo (some stands have multiple stand types, so we can't use STAND_ID)
stand_shp.insert(0, 'VELMA_ID', range(1, len(stand_shp) + 1))
# Export shp as csv for creating disturbance map based on stand IDs
stand_shp_csv = pd.DataFrame(stand_shp.drop(columns='geometry'))
stand_shp_csv.to_csv(config.stand_id_velma.parents[0] / 'disturbance_map.csv', index=False)

# Reproject to target CRS
proj = open(config.proj_wkt, 'r').read()
stand_shp = stand_shp.to_crs(proj)
updated_shp = config.stand_shp.parents[0] / 'Ellsworth_Stands_updated.shp'
stand_shp.to_file(updated_shp)
