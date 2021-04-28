Eco-hydrological modeling of the Ellsworth Preserve using the EPA's VELMA model
==============================
Requires only the EPA's VELMA program (Java executable). Some data downloaded using Google Earth Engine. File pre-processing and analysis in Python 3.x, with some scripts requiring Python 2.x and the ArcPy package 
(and ArcGIS license). ArcGIS is only used for resampling and reprojecting rasters, so this can be done in another GIS
and the Python 3.x files used afterwards for further processing.

<center><img src="https://github.com/ianpdavies/PNW_VELMA/blob/36340bc58f56e13ffa9912839b313fb39d2d47a9/ellsworth_area.PNG" width="35%" height="35%"></center>

Background:
------------
This study examined the ecological effects of different forest management scenarios in the Ellsworth Preserve maintained by The Nature Conservancy in southwestern Washington. We used the VELMA model developed by the EPA to simulate soil, water, and land cover changes in the watershed from 1984-2100. 

This repository includes the processing and analysis scripts used for this project until my departure from The Nature Conservancy in May 2021.

Set up notes
------------
 - Download the [VELMA .jar executable](https://www.epa.gov/water-research/visualizing-ecosystem-land-management-assessments-velma-model-20). Check in with the software authors (Bob McKane et al.) to ensure that you have the latest .jar file, and to ask for any supplementary tutorials and files.
 - The Python scripts require a specific directory system for input and output files. Individual files are accessed
  via the paths in the `config.py` file, so ensure those are correct for your system before running any scripts.

```bash
tnc_velma
├── data
│   ├── ellsworth_velma
│   ├── hydrology
│   ├── landcover
│   ├── precip
│   ├── soil
│   ├── temp
│   ├── topography
│   └── vector
├── models
├── notebooks
│   ├── archived
├── results
├── scripts
│   ├── analysis
│   ├── archived
│   └── javascript
├── tnc_velma
└── velma
    └── xml
```

Data:
------------
<details>
  <summary>Data requirements and examples</summary>
 Please see the VELMA user manual for required data files. This is a list of the data used in this project, and
 tips for downloading and processing them.

1. Soil
    * [STATSGO2 and gSSURGO](https://nrcs.app.box.com/v/soils) can be used to create a soil texture map. There are gaps in both datasets, so you may need to merge them using the `soil.py` script. They are database files that require some preprocessing to access the texture values.         
2. DEM
    * Downloaded from the [USGS](https://apps.nationalmap.gov/downloader). We used the 1/3 arc-second (10m) DEM that [covered the Ellsworth Preserve](https://www.sciencebase.gov/catalog/item/5f77838982ce1d74e7d6c0bd).
3. Climate drivers
    * PRISM daily temperature and precipitation measurements were downloaded from Google Earth Engine using the `daily_climate_drivers.js` script. VELMA simulated runoff actually matched observed runoff better when the PRISM precipitation was averaged with data from the nearby [Naselle rain gauge](https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USC00455774/detail). Other gauges can be found [here](https://gis.ncdc.noaa.gov/maps/clim/summaries/daily).
4. Future climate projections
    * Temperature and precipitation projections to 2100 from various GCMs were shared by the University of Washington Climate Impacts Group.
5. Land cover
    * Cover type was mapped using the National Land Cover Dataset ([NLCD](https://www.mrlc.gov/data)) as well as NOAA C-CAP. For simplicity though, all of Ellsworth was marked as conifer in VELMA, and the NLCD/C-CAP data was used to produce the permeability map.
    * Cover age for forest stands was mapped by TNC.
    * Biological parameters for cover types used in VELMA were copied from the .xml configuration files of previous VELMA studies. Inquire with the VELMA maintainers.



</details>


Script directory:
------------
<details>
  <summary>Script descriptions and processing order</summary>
 This is the order in which the scripts must be run during processing.
 
 Bolded scripts are written for Python 3.x. Scripts that are bolded and italicized and marked with an * are written for 
 Python 2.x and ArcPy.

* ****dem_resample.py:*** Resamples the DEM to a specified spatial resolution. NOTE: The resampled DEM must then be flat-processed in the JPDEM program created by the VELMA team. That flat-processed DEM is then used as the template for all the other rasters processed in the following scripts.
* ****soil.py:*** Creates a soil texture map by merging gSSURGO and STATSGO2
* ****cover.py:*** Resamples cover rasters to match DEM
* **cover_edit_stands.py:** Edits the Ellsworth stand shapefile in preparation for rasterization
* **cover_rasterize_stands.py:** Rasterizes the stand shapefile into stand age, type, and ID. Also rasterizes the experimental basins. 
* ****other_layers.py:*** Resamples all other rasters to match DEM
* **cover_combine_ccap.py:** Combines CCAP and NLCD land cover rasters to create one cover file
* **cover_permeability.py:** Creates a permeability map based on merged cover file
* **disturbances.py:** Creates filter maps for harvest disturbances
* **disturbances_randomize_clearcuts.py:** For clearcut scenario. Randomly samples clearcuts to only occur over x% of the watershed each year, rather than all at once
* **disturbances_historical.py:** Creates filter maps for historical disturbances, like blow-downs, based on the Hansen Global Forest Loss Dataset and the stand age map
* **cover_age.py:** Creates an initial cover age map for a given simulation starting year
* **velma_format_check.py:** Checks that all final rasters match the DEM resolution
* **export_VICWRF_avgs.py:** Averages simulation runs of the coupled WRF/VIC climate models, then exports precipitation and temperature files.
* **export_GCM.py:** Exports precipitation and temperature data for a specified GCM and time period. 
* **export_PRISM.py:** Exports observed precipitation and temperature data from PRISM for a given time period.
* **export_runoff.py:** Converts observed runoff to from cfs to mm, and adds in a dummy year of zeroes if specified.

Other scripts:

* **streamtemp_correct.py:** Trains and saves the regression model used to corrected seasonal biases in VELMA's stream temperature estimates.
* **edit_velma_parameters.py:** Used to batch edit parameters in multiple .xml configuration files for VELMA simulations
* **simulation_metrics.py:** Exports key calibration figures into a .csv for easy comparison across simulations
* **scenario_results_figs.py:** Exports figures of simulation results across forest management scenarios using different GCMs
* **scenario_results_figs.py:** Same as `scenario_results_figs.py` except for a historical period, and includes observed PRISM data as well as GCMs.

Earth Engine Javascript scripts:

* **daily_climate_drivers.js:** Exports a .csv of daily observed precipitation and temperature measurements for a specified study area and time period. Can export other climatic data as well, if desired.
* **clearcut_estimate.js:** Exports a .tif of the Hansen Global Forest Loss dataset for a specified area. 
     
</details>

Author:
------------
Ian P. Davies - *maintained until 5/1/2021* - https://github.com/ianpdavies




