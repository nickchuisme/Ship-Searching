#-*- coding: utf-8 -*-
import osr, csv, os
import fiona
import datetime, time
from shapely import geometry
from shapely.geometry import shape, Point
from rtree import index
from osgeo import ogr


class tree():
	def __init__(self):
		pass

	def createindex(self):
		#import data
		collection = fiona.open('C:/Users/USER/Desktop/rtree/taichung_fix.shp')
		for num,f in enumerate(collection):
			mmsi  = int(f['properties']['MMSI'])
			MMSI.append(mmsi)
			shapes[num] = shape(f['geometry'])
			properties[num] = f['properties']
			#print(num,properties[num]['End_time'])
			End_timeList.append(properties[num]['End_time'])
			Start_timeList.append(properties[num]['Start_time'])
		#insert index
		for number,line in enumerate(shapes.items()):
			#print(number)
			idx.insert(number, line[1].bounds)
		
		
	def FindOverlap(self,minX,minY,maxX,maxY):
		#get index
		callindex = tree.createindex()
		input_boundingBox = (minX,minY,maxX,maxY)
		boundingBoxList = [Point(minX,minY),Point(minX,maxY),Point(maxX,maxY),Point(maxX,minY)]
		poly = geometry.Polygon([[p.x, p.y] for p in boundingBoxList])
		print('BoundingBox: %s')%(poly)
		#select the intersect target
		#print('mmsi= %s')%(MMSI)
		
		##########
		
		spatialref = osr.SpatialReference()  # Set the spatial ref.
		spatialref.SetWellKnownGeogCS('WGS84')  # WGS84 aka ESPG:4326
		#create output Layer
		driver = ogr.GetDriverByName("ESRI Shapefile")
		outShapefile = 'C:/Users/USER/Desktop/rtree/rtreeshp.shp'
		# Remove output shapefile if it already exists
		if os.path.exists(outShapefile):
			driver.DeleteDataSource(outShapefile)
		dstfile = driver.CreateDataSource(outShapefile) # Your output file
		dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=ogr.wkbLineString) 

		# Add the other attribute fields needed with the following schema :
		fielddef = ogr.FieldDefn("MMSI", ogr.OFTString)
		fielddef.SetWidth(10)
		dstlayer.CreateField(fielddef)
		
		fielddef = ogr.FieldDefn("Start_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
	
		fielddef = ogr.FieldDefn("End_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
		
		############
		
		for x,linestring in zip(sorted(list(idx.intersection(input_boundingBox))),shapes.items()):
			#time.sleep(0.01)
			
			if (poly.intersects(linestring[1]) == True and tree.checktime(Start_timeList[x],End_timeList[x],format,x) == True):
				print('%s (%s) is selected...')%(x,MMSI[x])
				SelectedList.append(int(x))
				#print (x)
				#print(linestring[1])
				#print('start time:%s')%(Start_timeList[x])
				#print('end time:%s')%(End_timeList[x])
				#print('dstlayer in overlap = %s')%(dstlayer)
				#line = ogr.Geometry(ogr.wkbLineString)
				line= ogr.CreateGeometryFromWkt(str(linestring[1]))
				#print('line = %s')%(line)
				feature = ogr.Feature(dstlayer.GetLayerDefn())
				feature.SetGeometry(line)
				feature.SetField("MMSI", MMSI[x])
				feature.SetField("Start_time", str(Start_timeList[x]))
				feature.SetField("End_time", str(End_timeList[x]))
				feature.SetStyleString("PEN(c:#000000FF)")
				dstlayer.CreateFeature(feature)
			else:
				print('%s (%s) is not used...')%(x,MMSI[x])
		print('SelectedList: %s')%(SelectedList)
		print('Length of SelectedList: %s')%(len(SelectedList))
		
		#feature = ogr.Feature(dstlayer.GetLayerDefn())
		polygon = ogr.CreateGeometryFromWkt(str(poly))
		feature.SetGeometry(polygon)
		feature.SetField("MMSI", 'boundingbox')
		feature.SetField("Start_time", 'None')
		feature.SetField("End_time", 'None')
		#feature.SetStyleString("PEN(c:FF0000FF)")
		dstlayer.CreateFeature(feature)

	def checktime(self,From_time,To_time,date_format,id):
		if(date_format == 1):
			date_format = '%Y-%m-%d %H:%M:%S'
		elif(date_format == 2):
			date_format = '%Y/%m/%d %H:%M:%S'
		else:
			date_format = raw_input('input format: ')
		global LeftTimeBounding, RightTimeBounding
		#print('LeftTimeBounding = %s')%(LeftTimeBounding)
		#print('RightTimeBounding = %s')%(RightTimeBounding)
		#print('From_time = %s')%(From_time)
		#print('To_time = %s')%(To_time)
		
		if((type(LeftTimeBounding) == float) is False):
			LeftTimeBounding = time.mktime(time.strptime(str(LeftTimeBounding),date_format))
			RightTimeBounding = time.mktime(time.strptime(str(RightTimeBounding),date_format))
		From_time = time.mktime(time.strptime(From_time,date_format))
		To_time = time.mktime(time.strptime(To_time,date_format))
		
		#select time overlap
		if((From_time>RightTimeBounding) is False or (To_time<LeftTimeBounding) is False):
			#print('%s is selected...')%(id)
			return True
		
		
	
idx = index.Index()
shapes = {}
properties = {}
MMSI=[]
SelectedList = []
End_timeList=[]
Start_timeList=[]
date_format = 0

tree = tree()
#LeftTimeBounding = raw_input()
#RightTimeBounding = raw_input()
#format = int(input())
LeftTimeBounding = '2000/01/01 00:00:00'
RightTimeBounding = '2020/01/01 00:00:00'
format = 2

separator = ' '
minX,minY,maxX,maxY = raw_input("input minX,minY,maxX,maxY and divide with Space: ").split(separator)
tree.FindOverlap(float(minX),float(minY),float(maxX),float(maxY))