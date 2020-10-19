from pathlib import Path

project_path = Path(__file__).absolute().parents[1]
data_path = project_path / 'data'

# Download geomorphometry and gradient metrics toolbox here:
# https://evansmurphy.wixsite.com/evansspatial/arcgis-gradient-metrics-toolbox
geomorph_tbx_path = data_path.parents[0] / 'tools' / 'Geomorphometry & Gradient Metrics  (version 2.0)' / 'Geomorphometry and Gradient Metrics (version 2.0).tbx'

# ======================================================================================================================
# Ellsworth Preserve files

# Workflow: pre-DEM prep --> format files to DEM --> get files into VELMA-acceptable format

# Pre-DEM prep
stand_shp = data_path / 'landcover' / 'stands' / 'Ellsworth_TNC_Stands_2020.shp'  # Convert to raster of species IDs

# Input data files for DEM formatting (reproject, resample, clip to DEM)
study_area = data_path / 'vector' / 'ellsworth' / 'elcr_boundary.shp'
# dem = data_path / 'topography' / 'ellsworth' / 'USGS_1_n47w124.tif'  # Might need to mosaic if there are multiple DEMs
dem = data_path / 'topography' / 'ellsworth' / 'Surfaces_byTNC_v2007' / 'be_ellsworth_dem_filled_10m.tif'
fac = data_path / 'topography' / 'ellsworth' / 'HRNHDPlusRasters1708' / 'fac.tif'  # Might not be able to downsample this
nlcd = data_path / 'landcover' / 'nlcd' / 'NLCD_2016_Land_Cover_L48_20190424' / 'NLCD_2016_Land_Cover_L48_20190424.img'
stand_type = data_path / 'landcover' / 'stands' / 'ellsworth_stand_type.tif'
stand_age = data_path / 'landcover' / 'stands' / 'ellsworth_stand_age.tif'
stand_id = data_path / 'landcover' / 'stands' / 'ellsworth_stand_id.tif'
biomass = data_path / 'landcover' / 'emapr' / 'ellsworth' / 'waorca_biomass_ARD_tile_h02v02' / 'waorca_biomass_ARD_tile_h02v02.tif'
imperv = data_path / 'landcover' / 'emapr' / 'ellsworth' / 'waorca_impervious_cover_ARD_tile_h02v02' / 'waorca_impervious_cover_ARD_tile_h02v02.tif'
soil = data_path / 'soil' / 'gSSURGO_WA' / 'gSSURGO_WA.gdb' / 'MapunitRaster_10m'
prism_temp = data_path / 'temp' / 'PRISM_tmean_30yr_normal_4kmM2_annual_asc' / 'PRISM_tmean_30yr_normal_4kmM2_annual_asc.asc'
prism_precip = data_path / 'precip' / 'PRISM_ppt_30yr_normal_4kmM2_annual_asc' / 'PRISM_ppt_30yr_normal_4kmM2_annual_asc.asc'

# Output data files after DEM formatting
dem_out = dem.parents[0] / 'dem_ells.tif'
fac_out = fac.parents[0] / 'fac_ells.tif'
nlcd_out = nlcd.parents[0] / 'nlcd_ells.tif'
stand_type_out = stand_type.parents[0] / 'stand_type_ells.tif'
stand_age_out = stand_age.parents[0] / 'stand_age_ells.tif'
stand_id_out = stand_type.parents[0] / 'stand_id_ells.tif'
biomass_out = biomass.parents[0] / 'waorca_biomass_ells.tif'
imperv_out = imperv.parents[0] / 'waorca_imperv_ells.tif'
soil_out = soil.parents[0] / 'MapunitRaster_ells'
prism_temp_out = prism_temp.parents[0] / 'PRISM_temp_30yr_ells.tif'
prism_precip_out = prism_precip.parents[0] / 'PRISM_ppt_30yr_ells.tif'
hli_out = data_path / 'topography' / 'ellsworth' / 'hli_ells.tif'

# VELMA-format files
velma_data = data_path / 'ellsworth_velma'
dem_velma = velma_data / 'topography' / 'dem.asc'
fac_velma = velma_data / 'topography' / 'fac.asc'
nlcd_velma = velma_data / 'landcover' / 'nlcd.asc'
stand_type_velma = velma_data / 'landcover' / 'species_type.tif'
stand_age_velma = velma_data / 'landcover' / 'species_age.tif'
dist_velma = velma_data / 'landcover' / 'disturbances.tif'
biomass_velma = velma_data / 'landcover' / 'waorca_biomass.asc'
imperv_velma = velma_data / 'landcover' / 'waorca_imperv.asc'
soil_velma = velma_data / 'soil' / 'MapunitRaster_10m.asc'
prism_temp_velma = velma_data / 'temp' / 'PRISM_temp_30yr.asc'
prism_precip_velma = velma_data / 'precip' / 'PRISM_ppt_30yr.asc'
hli_velma = velma_data / 'topography' / 'hli.asc'

