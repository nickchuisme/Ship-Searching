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
		self.idx = index.Index()
		self.MMSI=[]
		self.SelectedList = []
		self.End_timeList=[]
		self.Start_timeList=[]
		self.date_format = 1
		self.shapes = {}
		self.properties = {}
		
	def createindex(self):
		#import data
		collection = fiona.open('C:/Users/USER/Desktop/rtree/taichung_fix.shp')
		for num,f in enumerate(collection):
			mmsi  = int(f['properties']['MMSI'])
			self.MMSI.append(mmsi)
			self.shapes[num] = shape(f['geometry']) 
			self.properties[num] = f['properties']
			self.End_timeList.append(self.properties[num]['End_time'])
			self.Start_timeList.append(self.properties[num]['Start_time'])
		#insert index
		for number,line in enumerate(self.shapes.items()):
			self.idx.insert(number, line[1].bounds)
		
	# 找重疊(第一次找線的bounding box與輸入之bounding box 第二次找線和輸入之bounding box)
	def FindOverlap(self,minX,minY,maxX,maxY):
		#get index
		callindex = tree.createindex()
		input_boundingBox = (minX,minY,maxX,maxY)
		boundingBoxList = [Point(minX,minY),Point(minX,maxY),Point(maxX,maxY),Point(maxX,minY)]
		poly = geometry.Polygon([[p.x, p.y] for p in boundingBoxList])
		print('BoundingBox: %s'%(poly)) 
	
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
		for x in sorted(list(self.idx.intersection(input_boundingBox))):
			#print(x)
			linestring=self.shapes[x]
			
			if (poly.intersects(linestring) == True and \
				tree.checktime(self.Start_timeList[x],self.End_timeList[x],date_format,x) == True):
				
				print('%s (%s) is selected...'%(x,self.MMSI[x]))
				self.SelectedList.append(int(x))
				line= ogr.CreateGeometryFromWkt(str(linestring))
				feature = ogr.Feature(dstlayer.GetLayerDefn())
				feature.SetGeometry(line)
				feature.SetField("MMSI", self.MMSI[x])
				feature.SetField("Start_time", str(self.Start_timeList[x]))
				feature.SetField("End_time", str(self.End_timeList[x]))
				feature.SetStyleString("PEN(c:#000000FF)")
				dstlayer.CreateFeature(feature)
			else:
				print('%s (%s) is not used...'%(x,self.MMSI[x]))
		
		print('SelectedList: %s'%(self.SelectedList))
		print('Length of SelectedList: %s'%(len(self.SelectedList)))
		
		polygon = ogr.CreateGeometryFromWkt(str(poly))
		feature.SetGeometry(polygon)
		feature.SetField("MMSI", 'boundingbox')
		feature.SetField("Start_time", 'None')
		feature.SetField("End_time", 'None')
		#feature.SetStyleString("PEN(c:FF0000FF)")
		dstlayer.CreateFeature(feature)

	# 檢查時間
	def checktime(self,From_time,To_time,date_format,id):
		global LeftTimeBounding, RightTimeBounding
		if(date_format == 1):
			date_format = '%Y-%m-%d %H:%M:%S'
		elif(date_format == 2):
			date_format = '%Y/%m/%d %H:%M:%S'
		if((type(LeftTimeBounding) == float) is False):
			LeftTimeBounding = time.mktime(time.strptime(str(LeftTimeBounding),date_format))
			RightTimeBounding = time.mktime(time.strptime(str(RightTimeBounding),date_format))
		From_time = time.mktime(time.strptime(From_time,date_format))
		To_time = time.mktime(time.strptime(To_time,date_format))
		
		#select time overlap
		if((From_time>LeftTimeBounding) and (To_time<RightTimeBounding)):
			return True


if __name__ == "__main__":
	tree = tree()
	LeftTimeBounding = raw_input("StartingTime: ")
	RightTimeBounding = raw_input("EndTime: ")
	date_format = int(raw_input("Timeformat[input 1.-, 2./]: "))

	minX,minY,maxX,maxY = raw_input("input minX,minY,maxX,maxY and divide with Space: ").split(' ')
	tree.FindOverlap(float(minX),float(minY),float(maxX),float(maxY))
