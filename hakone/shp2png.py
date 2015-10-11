#!/usr/bin/env python
# -*- coding: utf-8 -*-

# depend on PIL on python2.7 by sudo port install py27-pil
# depend on gdal

# target shapefile (polygon/line)
in_file_name = "shapefile.shp"
# output image
out_file_name = "uv_texture.png"
imageWidth, imageHeight = 4096, 4096
# clip area lon/lat
north, east, west, south = 46, 149, 127, 25
print "hapefile must be WGS84 or JDG2000"

"""
OGRwkbGeometryType { 
  wkbUnknown = 0, wkbPoint = 1, wkbLineString = 2, wkbPolygon = 3, 
  wkbMultiPoint = 4, wkbMultiLineString = 5, wkbMultiPolygon = 6, wkbGeometryCollection = 7, 
  wkbNone = 100, wkbLinearRing = 101, wkbPoint25D = 0x80000001, wkbLineString25D = 0x80000002, 
  wkbPolygon25D = 0x80000003, wkbMultiPoint25D = 0x80000004, wkbMultiLineString25D = 0x80000005, wkbMultiPolygon25D = 0x80000006, 
  wkbGeometryCollection25D = 0x80000007 
}
"""

import math, sys
from PIL import Image, ImageDraw
from osgeo import ogr

multi_x = imageWidth / (east - west)
multi_y = imageHeight / (north - south)
def fX(n):
    return (n -  west) * multi_x
def fY(n):
    return (north - n) * multi_y
def getColor(r,g,b):
    return (r,g,b)

im = Image.new("RGB", (imageWidth, imageHeight), (0, 0, 0))
canvas = ImageDraw.Draw(im)

shape = ogr.Open(in_file_name)
layer = shape.GetLayer()
print layer.GetSpatialRef().ExportToProj4()

print "field definitions:"
feature_defn = layer.GetLayerDefn()
for i in range(feature_defn.GetFieldCount()):
    field_defn = feature_defn.GetFieldDefn(i)
    print field_defn.GetName()

nCountPolygon = 0
nCountLineString = 0
for nFeature in range(layer.GetFeatureCount()):
    feature = layer.GetFeature(nFeature)
    geometryRef = feature.GetGeometryRef()
    if not feature.GetField(0):
        continue
    # GetFieldで付加データ
    for nGeometry in range(geometryRef.GetGeometryCount()):
        geometry = geometryRef.GetGeometryRef(nGeometry)
        if geometry.GetGeometryType() == ogr.wkbPolygon:
            print "ogr.wkbPolygon rings:%d" % (geometry.GetGeometryCount())
            nCountPolygon += 1
            for nRing in range(geometry.GetGeometryCount()):
                ring = geometry.GetGeometryRef(nRing)
                # print ring
                coords = list()
                for nPoint in range(ring.GetPointCount() - 1):
                    point = ring.GetPoint(nPoint)
                    coords.append(fX(point[0]))
                    coords.append(fY(point[1]))
                if len(coords) > 2:
                    canvas.polygon(coords, fill=getColor(255,255,255), outline=getColor(0,0,0))
        elif geometry.GetGeometryType() == ogr.wkbLineString:
            if geometry.GetPointCount() > 0:
                print "%s : ogr.wkbLineString %d" % (feature.GetField(0), geometry.GetPointCount())
            # print "ogr.wkbLineString has " + str(geometry.GetPointCount()) + " points"
            nCountLineString += 1
            coords = list()
            for nPoint in range(geometry.GetPointCount() - 1):
                point = geometry.GetPoint(nPoint)
                coords.append(fX(point[0]))
                coords.append(fY(point[1]))
                # print point, fX(point[0]), fY(point[1])
            if len(coords) > 1:
                canvas.polygon(coords, fill=getColor(255,255,255), outline=getColor(0,0,0))
        elif geometry.GetGeometryType() == ogr.wkbMultiPolygon:
            print "NOT IMPLEMENTED ogr.wkbMultiPolygon"
        elif geometry.GetGeometryType() == ogr.wkbMultiLineString:
            print "NOT IMPLEMENTED ogr.wkbMultiLineString"
        else:
            print "NOT IMPLEMENTED"

im.save(out_file_name, "PNG")
print "Polygon drawn:", nCountPolygon
print "LineString drawn:", nCountLineString
