import numpy as np
import pandas as pd
import os
from natsort import natsorted
import config
import itertools
import xml.etree.ElementTree as ET

# =======================================================================

xml_root = config.data_path.parents[0] / 'xml'

scenarios = ['baseline', 'historical', 'active_all', 'ind_clearcut']
# scenarios = ['historical']

# values_dict = {'calibration/VelmaCalibration.properties/be': 0.95,
#                'soil/siltloam/setSoilLayerWeights': '0.19, 0.22, 0.26, 0.33',
#                'soil/siltloam/surfaceKs': 4000,
#                'soil/siltloam/ksLateralExponentialDecayFactor': 0.00135,
#                'soil/siltloam/ksVerticalExponentialDecayFactor': 0.002,
#                'soil/siltloam/soilColumnDepth': 3000,
#                'soil/siltyclayloam/setSoilLayerWeights': '0.19, 0.22, 0.26, 0.33',
#                'soil/siltyclayloam/surfaceKs': 3800,
#                'soil/siltyclayloam/ksLateralExponentialDecayFactor': 0.00135,
#                'soil/siltyclayloam/ksVerticalExponentialDecayFactor': 0.00175,
#                'soil/siltyclayloam/soilColumnDepth': 3000}

# values_dict = {'disturbance/restoration_pct/biomassAgStemNoffsiteFraction': 0,
#                'disturbance/restoration_pct/biomassBgStemNoffsiteFraction': 0,
#                'disturbance/restoration_pct/biomassLeafNoffsiteFraction': 0,
#                'disturbance/restoration_pct/biomassRootNoffsiteFraction': 0,
#                'disturbance/restoration_pct/ageThreshold': '15-15',
#                'disturbance/restoration_thin1st/biomassAgStemNoffsiteFraction': 0.85,
#                'disturbance/restoration_thin1st/biomassBgStemNoffsiteFraction': 0,
#                'disturbance/restoration_thin1st/biomassLeafNoffsiteFraction': 0,
#                'disturbance/restoration_thin1st/biomassRootNoffsiteFraction': 0,
#                'disturbance/restoration_thin1st/ageThreshold': '40-40',
#                'disturbance/restoration_thin2nd/biomassAgStemNoffsiteFraction': 0.85,
#                'disturbance/restoration_thin2nd/biomassBgStemNoffsiteFraction': 0,
#                'disturbance/restoration_thin2nd/biomassLeafNoffsiteFraction': 0,
#                'disturbance/restoration_thin2nd/biomassRootNoffsiteFraction': 0,
#                'disturbance/restoration_thin2nd/ageThreshold': '60-60',
#                'disturbance/restoration_thin3rd/biomassAgStemNoffsiteFraction': 0.85,
#                'disturbance/restoration_thin3rd/biomassBgStemNoffsiteFraction': 0,
#                'disturbance/restoration_thin3rd/biomassLeafNoffsiteFraction': 0,
#                'disturbance/restoration_thin3rd/biomassRootNoffsiteFraction': 0,
#                'disturbance/restoration_thin3rd/ageThreshold': '80-80'}

values_dict = {'spatialDataWriter/co2_sum/initializeActiveYears': 9999,
               'spatialDataWriter/biomass_ag_stem/initializeActiveYears': 9999,
               'spatialDataWriter/biomass_delta_ag_stem/initializeActiveYears': 9999,
               'spatialDataWriter/biomass_offsite/initializeActiveYears': 9999,
               'spatialDataWriter/biomass_c/initializeActiveYears': 9999,
               'spatialDataWriter/total_detritus_nitrogen/initializeActiveYears': 9999,
               'spatialDataWriter/total_detritus_carbon/initializeActiveYears': 9999,
               'spatialDataWriter/water_stored/initializeActiveYears': 9999}

params = values_dict.keys()
values = values_dict.values()

for scenario in scenarios:
    scenario_path = xml_root / scenario
    sims = os.listdir(scenario_path)
    for sim in sims:
        xml_path = scenario_path / sim
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for param, value in zip(params, values):
            for item in root.findall(param):
                item.text = str(value)
        tree.write(xml_path)
