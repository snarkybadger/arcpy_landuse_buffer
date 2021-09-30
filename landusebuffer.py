# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 13:18:15 2020

@author: grox1678
"""

import arcpy
from arcpy import env
env.workspace = r'D:\data'
env.overwriteOutput = 1
theme = 'interestAreas.shp'
circle_buff = "circlebuff.shp"
square_buff = "squarebuff.shp"


print "Part One"
print "Calculating extent of three polygons and making mesh sampling distance"
ro = raw_input (["Choose circle or square buffer"])

if ro == "square":
    arcpy.Delete_management(square_buff)
    arcpy.Delete_management("aclip1.shp")
    arcpy.CreateFeatureclass_management(env.workspace,square_buff,'POLYGON')
    cursor = arcpy.da.SearchCursor(theme,"SHAPE@")
    point = arcpy.Point()
    l=arcpy.Array()
    counter = 0
    mesh = [2000,3500,4500]
    buildCur = arcpy.da.InsertCursor(square_buff,'SHAPE@')
    for row in cursor:
            ext = row[0]
            XMAX = ext.extent.XMax
            XMIN = ext.extent.XMin
            YMAX = ext.extent.YMax
            YMIN = ext.extent.YMin            
            for i in range(int(XMIN), int(XMAX), mesh[counter]):
                for y in range(int(YMIN), int(YMAX), mesh[counter]):
                    pointYmax=arcpy.Point()
                    pointYmax.X= i +500
                    pointYmax.Y= y -500
                    l.append(pointYmax)
                    pointXmax=arcpy.Point()
                    pointXmax.X= i +500
                    pointXmax.Y= y +500
                    l.append(pointXmax)
                    pointYmin=arcpy.Point()
                    pointYmin.X= i -500
                    pointYmin.Y= y +500
                    l.append(pointYmin)
                    pointXmin=arcpy.Point()
                    pointXmin.X= i -500
                    pointXmin.Y= y -500
                    l.append(pointXmin)
                    sqpoly = arcpy.Polygon(l)
                    buildCur.insertRow([sqpoly])
                    l.removeAll()          
            counter+=1                          
    arcpy.Clip_analysis(square_buff, theme, "aclip1.shp")
    del buildCur

if ro == "circle":
    arcpy.Delete_management(circle_buff)
    arcpy.Delete_management("circle_buff2.shp")
    arcpy.Delete_management("aclip1.shp")
    arcpy.CreateFeatureclass_management(env.workspace,circle_buff,'POLYGON')
    cursor = arcpy.da.SearchCursor(theme,"SHAPE@")
    point = arcpy.Point()
    l=arcpy.Array()
    mesh = [2000,3500,4500]
    counter = 0
    for row in cursor:
        ext = row[0]
        XMAX = ext.extent.XMax
        XMIN = ext.extent.XMin
        YMAX = ext.extent.YMax
        YMIN = ext.extent.YMin
        for i in range(int(XMIN), int(XMAX), mesh[counter]):
            for y in range(int(YMIN), int(YMAX), mesh[counter]):
                point.X=i
                point.Y=y
                l.append(point)
        counter+=1   
    multi=arcpy.Multipoint(l)
    arcpy.CreateFeatureclass_management(env.workspace,circle_buff,'MULTIPOINT')
    buildCur = arcpy.da.InsertCursor(circle_buff,['SHAPE@'])
    buildCur.insertRow([multi])
    del buildCur
    output = "D:\data\circlebuff2.shp"
    distance = "500 meters"
    arcpy.Buffer_analysis(circle_buff, output, distance)
    arcpy.Clip_analysis(theme, output, "aclip1.shp")

print "Apply zonal statistics to calculate intensity of land usage within buffer for 1992 and 2001"
arcpy.CheckOutExtension('SPATIAL')

#agr1992
inZoneData = "aclip1.shp"
zoneField = "Id"
inValueRaster = "agr1992"
outTable = "zonalstataoi92.dbf"
outZSat = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable)

#agr2001
inZoneData = "aclip1.shp"
zoneField = "Id"
inValueRaster = "agr2001"
outTable = "zonalstataoi02.dbf"
outZSat = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable)

print "Average intensity of agricultural land in 1992"
with arcpy.da.SearchCursor("zonalstataoi92.dbf", ["MEAN"]) as cursor:
    for row in cursor:
        print row[0]
print "Average intensity of agricultural land in 2001"
with arcpy.da.SearchCursor("zonalstataoi92.dbf", ["MEAN"]) as cursor:
    for row in cursor:
        print row[0]
