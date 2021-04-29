from pathlib import Path

project_path = Path(__file__).absolute().parents[1]
data_path = project_path / 'data'

# ======================================================================================================================
# Ellsworth Preserve files, 10m resolution

# Parameters
cell_size = "10 10"
proj_wkt = data_path / 'NAD_1983_UTM_Zone_10N.prj'
velma_data = data_path / 'ellsworth_velma'  # Output folder

# Text files
streamflow = data_path / 'hydrology' / 'ellsworth' / 'wa_ecy_gauge' / 'streamflow' / 'ells_streamflow_2003_2008.csv'
daily_ppt = data_path / 'precip' / 'ellsworth' / 'prism_ppt_1981_2020_daily.csv'
daily_temp_mean = data_path / 'temp' / 'ellsworth' / 'prism_temp_1981_2020_daily.csv'

# Shapefiles
study_area = data_path / 'vector' / 'ellsworth' / 'ells_upstream_clip.shp'
stand_shp = data_path / 'landcover' / 'stands' / 'Ellsworth_TNC_Stands_2020_extended.shp'  # Convert to raster of species IDs
flowlines = data_path / 'hydrology' / 'ellsworth' / 'NHDFlowline_Ellsworth_upstream.shp'
exp_basins = data_path / 'landcover' / 'stands' / 'experimental_basins_2010.shp'

# Input raster files
dem_raw = data_path / 'topography' / 'ellsworth' / 'Surfaces_byTNC_v2007' / 'be_ellsworth_dem.tif'
dem_border = data_path / 'topography' / 'ellsworth' / 'USGS_13_n47w124.tif'  # Used to pad smaller DEM if missing pixels
dem = data_path / 'topography' / 'ellsworth' / 'dem_merge.asc' # This goes to JPDEM to be flat-processed
gssurgo = data_path / 'soil' / 'gSSURGO_WA' / 'gSSURGO_WA.gdb' / 'MapunitRaster_10m'
statsgo2 = data_path / 'soil' / 'wss_gsmsoil_WA_[2016-10-13]' / 'wss_gsmsoil_WA_[2016-10-13]' / 'statsgo2_text'
nlcd = data_path / 'landcover' / 'nlcd' / 'NLCD_2016_Land_Cover_L48_20190424_yB0PwSKH1891ABtYbm88.tiff'
noaa_ccap = data_path / 'landcover' / 'noaa_ccap' / 'fromNOAA_lcWa10m' / 'wa_2016_ccap2-0_level1-0_temp01.img'
cover_type = data_path / 'landcover' / 'stands' / 'ellsworth_stand_type.tif'
cover_age = data_path / 'landcover' / 'stands' / 'ellsworth_stand_age.tif'
stand_id = data_path / 'landcover' / 'stands' / 'ellsworth_stand_id.tif'
yearly_forest_loss = data_path / 'landcover' / 'yearly_forest_loss.tif'

# Output ASCII files
velma_data = data_path / 'ellsworth_velma'
dem_velma = velma_data / 'topography' / 'dem.asc'
nlcd_velma = velma_data / 'landcover' / 'nlcd.asc'
cover_type_velma = velma_data / 'landcover' / 'cover_type.asc'
cover_type_nlcd_merge_velma = velma_data / 'landcover' / 'cover_type_merge_nlcd.asc'  # Stands + NLCD cover
cover_type_ccap_merge_velma = velma_data / 'landcover' / 'cover_type_merge_ccap.asc'  # Stands + NLCD cover
cover_age_velma = velma_data / 'landcover' / 'cover_age.asc'
stand_id_velma = velma_data / 'landcover' / 'stand_id.asc'
exp_basins_velma = velma_data / 'landcover' / 'experimental_basins_2010.asc'
soil_velma = velma_data / 'soil' / 'MapunitRaster_10m.asc'
noaa_ccap_velma = velma_data / 'landcover' / 'noaa_ccap.asc'
yearly_forest_loss_velma = velma_data / 'landcover' / 'yearly_forest_loss.asc'
