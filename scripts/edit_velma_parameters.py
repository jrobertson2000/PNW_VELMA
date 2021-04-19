import numpy as np
import pandas as pd
import os
from natsort import natsorted
import config
import itertools
import xml.etree.ElementTree as ET
# =======================================================================

xml_root = config.data_path.parents[0] / 'velma' / 'xml'

scenarios = ['baseline', 'historical', 'ind_clearcut', 'restoration_active_all']

values_dict = {'calibration/VelmaCalibration.properties/be': 0.95,
               'soil/siltloam/setSoilLayerWeights': '0.19, 0.22, 0.26, 0.33',
               'soil/siltloam/surfaceKs': 4000,
               'soil/siltloam/ksLateralExponentialDecayFactor': 0.00135,
               'soil/siltloam/ksVerticalExponentialDecayFactor': 0.002,
               'soil/siltloam/soilColumnDepth': 3000,
               'soil/siltyclayloam/setSoilLayerWeights': '0.19, 0.22, 0.26, 0.33',
               'soil/siltyclayloam/surfaceKs': 3800,
               'soil/siltyclayloam/ksLateralExponentialDecayFactor': 0.00135,
               'soil/siltyclayloam/ksVerticalExponentialDecayFactor': 0.00175,
               'soil/siltyclayloam/soilColumnDepth': 3000}

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
