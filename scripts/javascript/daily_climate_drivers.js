// Google Earth Engine script
// Exports daily averages of climate driver datasets over a given ROI as .csv files
// Author: Ian P. Davies
// Date: 26 April 2021

// This ROI can be imported from a FeatureCollection via an uploaded shapefile, or just drawn in Earth Engine
var roi = ee.FeatureCollection("users/ianpdavies/ellsworth_boundary")

function get_daily_means(image_col, geometry, method){
  // Calculates daily average of image_col over geometry using method
  // Collect date/image as feature collection
  var daily_avgs_fc = IC.map(function(image) {
    return image.reduceRegions({
      collection: geometry,
      reducer: ee.Reducer.mean(),
      // scale: 30
    }).filter(ee.Filter.neq('mean', null))
      .map(function(f) {
        return f.set('date', image.date().format('MM-dd-yyyy'));
      });
  }).flatten();

  var rows = daily_avgs_fc.distinct('date');
  var daily_avgs = ee.Join.saveAll('matches').apply({
    primary: rows,
    secondary: daily_avgs_fc,
    condition: ee.Filter.equals({
      leftField: 'date',
      rightField: 'date'
    })
  });

  var means = daily_avgs.aggregate_array('mean')
  var dates = daily_avgs.aggregate_array('date')
  var zipped = dates.zip(means)

  var table = ee.FeatureCollection(zipped.map(function(row){
    var date = ee.List(row).get(0)
    var mean = ee.List(row).get(1)
    return ee.Feature(null).set('Date', date, 'Mean', mean)
  }))

  return table
}

var startDate = ee.Date('1981-01-01')
var endDate = ee.Date('2021-01-01')
Map.addLayer(roi)

//=============================================
// Daily avg precip estimates
var prism_ppt = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
  .filterBounds(roi)
  .filterDate(startDate, endDate)
  .select('ppt')

var daily = get_daily_means(prism_ppt, roi)

Export.table.toDrive({
  collection: daily,
  description: 'prism_ppt_1981_2020_daily',
  fileNamePrefix: 'prism_ppt_1981_2020_daily',
  fileFormat: 'CSV'
});

//=============================================
// Daily avg temp estimates
var prism_temp = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
  .filterBounds(roi)
  .filterDate(startDate, endDate)
  .select('tmean')

var daily = get_daily_means(prism_temp, roi)

Export.table.toDrive({
  collection: daily,
  description: 'prism_temp_1981_2020_daily',
  fileNamePrefix: 'prism_temp_1981_2020_daily',
  fileFormat: 'CSV'
});

// //=============================================
// // Daily min temp estimates
// var prism_temp = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('tmin')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'prism_temp_min_2000_2019_daily',
//   fileNamePrefix: 'prism_temp_min_2000_2019_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Daily max temp estimates
// var prism_temp = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('tmax')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'prism_temp_max_2000_2019_daily',
//   fileNamePrefix: 'prism_temp_max_2000_2019_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Evapotranspiration (PML)
// var pml_et = ee.ImageCollection("CAS/IGSNRR/PML/V2")
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('ET_water')

// var daily = get_daily_means(pml_et, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'pml_et_2002_2017_daily',
//   fileNamePrefix: 'pml_et_2002_2017_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Evapotranspiration (MODIS)
// var modis_et = ee.ImageCollection('MODIS/NTSG/MOD16A2/105')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('ET')

// var daily = get_daily_means(modis_et, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'modis_et_2000_2014',
//   fileNamePrefix: 'modis_et_2000_2014',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Potential latent heat flux (MODIS)
// var modis_et = ee.ImageCollection('MODIS/NTSG/MOD16A2/105')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('PLE')

// var daily = get_daily_means(modis_et, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'modis_plhf_2000_2014_daily',
//   fileNamePrefix: 'modis_plhf_2000_2014_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Daily min vapor pressure deficit (PRISM)
// var prism_temp = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('vpdmin')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'prism_vap_press_def_min_2000_2019_daily',
//   fileNamePrefix: 'prism_vap_press_def_min_2000_2019_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Daily max vapor pressure deficit (PRISM)
// var prism_temp = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('vpdmax')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'prism_vap_press_def_max_2000_2019_daily',
//   fileNamePrefix: 'prism_vap_press_def_max_2000_2019_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Daily mean dew point temp (PRISM)
// var prism_temp = ee.ImageCollection('OREGONSTATE/PRISM/AN81d')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('tdmean')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'prism_dewpoint_temp_2000_2019_daily',
//   fileNamePrefix: 'prism_dewpoint_temp_2000_2019_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Projected daily precipitation

// var startDate = ee.Date('2000-01-01')
// var endDate = ee.Date('2099-12-31')
// var prism_temp = ee.ImageCollection('NASA/NEX-GDDP')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('pr')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'nex_precip_2000_2099_daily',
//   fileNamePrefix: 'nex_precip_2000_2099_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Projected daily temp min

// var startDate = ee.Date('2000-01-01')
// var endDate = ee.Date('2099-12-31')
// var prism_temp = ee.ImageCollection('NASA/NEX-GDDP')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('tasmin')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'nex_temp_min_2000_2099_daily',
//   fileNamePrefix: 'nex_temp_min_2000_2099_daily',
//   fileFormat: 'CSV'
// });

// //=============================================
// // Projected daily temp max

// var startDate = ee.Date('2000-01-01')
// var endDate = ee.Date('2099-12-31')
// var prism_temp = ee.ImageCollection('NASA/NEX-GDDP')
//   .filterBounds(roi)
//   .filterDate(startDate, endDate)
//   .select('tasmax')

// var daily = get_daily_means(prism_temp, roi)

// Export.table.toDrive({
//   collection: daily,
//   description: 'nex_temp_max_2000_2099_daily',
//   fileNamePrefix: 'nex_temp_max_2000_2099_daily',
//   fileFormat: 'CSV'
// });