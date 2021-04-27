// Google Earth Engine script
// Exports a .tif of clearcut estimates from the Hansen dataset for a given ROI and period of time
// Author: Ian P. Davies
// Date: 26 April 2021

var roi = geometry

Map.addLayer(roi)

// Load Hansen tree cover
var gfcImage = ee.Image('UMD/hansen/global_forest_change_2019_v1_7');
var yearly_loss = gfcImage.select(['lossyear'])

// Output file is an integer .tif where the cell values correspond to the year in which forest loss occurred
// e.g. cell=12 means forest was lost in 2012

Export.image.toDrive
({
  image: yearly_loss,
  description: 'yearly_forest_loss',
  fileNamePrefix: 'yearly_forest_loss',
  region: roi,
  scale: 10
});
