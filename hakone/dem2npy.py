#!/usr/bin/env python
# -*- coding: utf-8 -*-

# extract height data from geotiff and save as binary
# check data type by using gdalinfo.  
# python dem2npy.py dem.tif


import sys, os, datetime, struct
from sets import Set
try:
  from osgeo import gdal, osr
  from gdalconst import *
except ImportError:
  import gdal
  from gdalconst import *

flush = sys.stdout.flush

import numpy as np

def main(argv=None):
  # option
  # gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
  # os.putenv("GDAL_FILENAME_IS_UTF8", "NO")  # for merging process

  driver = gdal.GetDriverByName("GTiff")
  if driver is None:
    return "Driver %s not found" % format

  nFiles = len(argv)
  if nFiles == 1:
    return "No input files selected"

  for i in range(1, nFiles):
    fin_name = argv[i]

    dataset = gdal.Open( fin_name, GA_ReadOnly )
    if dataset is None:
      return "GDAL File %s not found" % fin_name

    print dataset.GetMetadata()
    print "***************************"
    print 'Driver: ', dataset.GetDriver().ShortName,'/', dataset.GetDriver().LongName
    print 'nBand: ', dataset.RasterCount
    print 'Size is ',dataset.RasterXSize,'x',dataset.RasterYSize, 'x',dataset.RasterCount
    print 'Projection is ', dataset.GetProjection()

    proj = dataset.GetProjection()
    
    geotransform = dataset.GetGeoTransform()
    Origin = (geotransform[0], geotransform[3])
    xPitch, yPitch = geotransform[1], geotransform[5]
    nWidth, nHeight = dataset.RasterXSize, dataset.RasterYSize

    if not geotransform is None:
      print 'left,  top    = (%.10f, %.10f)' % (geotransform[0] ,geotransform[3])
      print 'right, bottom = (%.10f, %.10f)' % (geotransform[0]+geotransform[1]*nWidth ,geotransform[3]+geotransform[5]*nHeight)
      print 'Pixel Pitch = %.10f, %.10f'  % (geotransform[1], geotransform[5])

    bands = []
    for nBand in range( 1, dataset.RasterCount + 1 ):
      band = dataset.GetRasterBand(nBand)
      if band is None:
        continue

      print 'Band Type=',gdal.GetDataTypeName(band.DataType)

      minData = band.GetMinimum()
      maxData = band.GetMaximum()
      if minData is None or maxData is None:
        (minData, maxData) = band.ComputeRasterMinMax(1)
      print 'Band 1 range: Min=%.3f, Max=%.3f' % (minData, maxData)

      if band.GetOverviewCount() > 0:
        print 'Band has ', band.GetOverviewCount(), ' overviews.'

      if not band.GetRasterColorTable() is None:
        print 'Band has a color table with ', band.GetRasterColorTable().GetCount(), ' entries.'

      # print 'Band.XSize:', band.XSize, 'band.YSize:', band.YSize

      # ReadAsArray(self, xoff=0, yoff=0, win_xsize=None, win_ysize=None, buf_xsize=None, buf_ysize=None, buf_obj=None)
      # WriteArray(self, array, xoff=0, yoff=0)
      bandArray = band.ReadAsArray()
      print 'Band.XSize:', len(bandArray[0]), 'band.YSize:', len(bandArray)

      for x in range(len(bandArray)):
        for y in range(len(bandArray[x])):
          # data is multipled by 10 (because height values will be within int16 range)
          bandArray[x][y] = int(bandArray[x][y]*10)

      bands.append( bandArray )

    print "Size of Band:", len(bands)
    targetBand = 0
    targetType = np.int16
    print "raw write .. DEM.shape = ", bands[targetBand].shape
    print "original data type of Geotif", bands[targetBand].dtype
    """
      GDAL defines following data type;
      GDT_Unknown = 0, GDT_Byte = 1, GDT_UInt16 = 2, GDT_Int16 = 3, 
      GDT_UInt32 = 4, GDT_Int32 = 5, GDT_Float32 = 6, GDT_Float64 = 7, 
      GDT_CInt16 = 8, GDT_CInt32 = 9, GDT_CFloat32 = 10, GDT_CFloat64 = 11,
    """
    print "target data type of binary file", targetType
    """
    http://docs.scipy.org/doc/numpy/reference/arrays.scalars.html#arrays-scalars-built-in
    """
    bands[targetBand].astype(targetType).tofile(fin_name[:-4] + ".npy")



if __name__ == "__main__":
  main(sys.argv)
  sys.exit(0)
