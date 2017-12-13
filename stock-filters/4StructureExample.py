# This filter procedurally generates 4 structures within the selection box within defined limits
# This filter: mcgreentn@gmail.com (mikecgreen.com)

import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

#inputs are taken from the user. Here I've just showing labels, as well as letting the user define
# what the main creation material for the structures is
inputs = (
	("4Structures", "label"),
	("Material:", alphaMaterials.Cobblestone), # the material we want to use to build the mass of the structures
	("Creator: Michael Green", "label"),
	)

# Start Utility Functions #
# these are more for ease of use than anything else. Simple math functons that allow me to quickly set blocks, find distances, and sizes

def setBlockIfEmpty(level, (block, data), x, y, z):
    tempBlock = level.blockAt((int)(x),(int)(y),(int)(z))
    if tempBlock == 0:
		setBlock(level, (block, data), (int)(x),(int)(y),(int)(z))

def setBlock(level, (block, data), x, y, z):
	level.setBlockAt((int)(x),(int)(y),(int)(z), block)
    	level.setBlockDataAt((int)(x),(int)(y),(int)(z), data)


def setBlockToGround(level, (block, data), x, y, z, ymin):
    for iterY in xrange(ymin, (int)(y)):
    	setBlockIfEmpty(level, (block, data), (int)(x),(int)(iterY),(int)(z))


def getBoxSize(box):
	return (box.maxx - box.minx, box.maxy - box.miny, box.maxz - box.minz)

def fix(angle):
	while angle > pi:
		angle = angle - 2 * pi
	while angle < -pi:
		angle = angle + 2 * pi
	return angle

def drawLine(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1) ):
	drawLineConstrained(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), 0 )

def drawLineConstrained(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), maxLength ):
	dx = x1 - x
	dy = y1 - y
	dz = z1 - z

	distHoriz = dx*dx + dz*dz
	distance = sqrt(dy*dy + distHoriz)

	if distance < maxLength or maxLength < 1:
		phi = atan2(dy, sqrt(distHoriz))
		theta = atan2(dz, dx)

		iter = 0
		while iter <= distance:
			scratchpad.setBlockAt((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)), blockID)
			scratchpad.setBlockDataAt((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)), blockData)
			iter = iter+0.5 # slightly oversample because I lack faith.
# End Utility Functions #

# MAIN SECTION #
# Every agent must have a "perform" function, which has three parameters
# 1: the level (aka the minecraft world). 2: the box 3: input options from the user
def perform(level, box, options):
	quadrants = splitIntoQuadrants(box)
	# for each quadrant
	for quad in quadrants:
		buildFence(level, quad)
		buildStructure(level, quad)

#splits the given box into 4 unequal areas
def splitIntoQuadrants(box):
	(width, height, depth) = getBoxSize(box)
	centreWidth = width / 2
	centreDepth = depth / 2

	# a random modifier for quadrant splitting which is somewhere between 0 and 1/8 the total box width and depth
	randomWidth = random.randint(-(centreWidth / 4), centreWidth / 4)
	randomDepth = random.randint(-(centreDepth / 4), centreDepth / 4)

	# creating the new bounds
	newWidthBound = centreWidth + randomWidth
	newDepthBound = centreDepth + randomDepth

	#creating the outer edge bounds
	outsideWidthSize = width - newWidthBound - 1
	outsideDepthSize = depth - newDepthBound - 1

	# creating the bounding boxes
	# NOTE: BoundingBoxes are objects contained within pymclevel and can be instantiated as follows
	# BoundingBox((x,y,z), (sizex, sizey, sizez))
	# in this instance, you specifiy which corner to start, and then the size of the box dimensions
	one = BoundingBox((box.minx, box.miny, box.minz), (newWidthBound-1, box.maxy, newDepthBound-1))
	two = BoundingBox((box.minx+newWidthBound+1, box.miny, box.minz), (outsideWidthSize-1, box.maxy, newDepthBound-1))
	three = BoundingBox((box.minx, box.miny, box.minz+newDepthBound+1), (newWidthBound-1, box.maxy, outsideDepthSize-1))
	four = BoundingBox((box.minx+newWidthBound+1, box.miny, box.minz+newDepthBound+1), (outsideWidthSize-1, box.maxy, outsideDepthSize-1))
	boxList = [one, two, three, four]
	return boxList

# builds a wooden fence around the perimeter of this box, like this photo
#			  Top - zmax
#       ----------------
#       |              |
#       |              |
#       |              |
# Left  |              | Right
# xmin  |              | xmax
#       |              |
#       |              |
#       ----------------
#			Bottom - zmin
def buildFence(level, box):

	# side by side, go row/column by row/column, and move down the pillar in the y axis starting from the top
	# look for the first non-air tile (id != 0). The tile above this will be a fence tile

	# add top fence blocks
	for x in range(box.minx, box.maxx):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(x, y, box.maxz)
				if tempBlock != 0:
					newValue = 0
					setBlock(level, (85, newValue), x, y+1, box.maxz)
					break;
	# add bottom fence blocks (don't double count corner)
	for x in range(box.minx, box.maxx):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(x, y, box.minz)
				if tempBlock != 0:
					newValue = 0
					setBlock(level, (85, newValue), x, y+1, box.minz)
					break;
	# add left fence blocks (don't double count corner)
	for z in range(box.minz+1, box.maxz):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(box.minx, y, z)
				if tempBlock != 0:
					newValue = 0
					setBlock(level, (85, newValue), box.minx, y+1, z)
					break;
	# add right fence blocks
	for z in range(box.minz, box.maxz+1):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(box.maxx, y, z)
				if tempBlock != 0:
					newValue = 0
					setBlock(level, (85, newValue), box.maxx, y+1, z)
					break;

# builds a structure (the material of which is specified by user in inputs) within the given box
# 4 steps:
# 1. decide the floor plan, map out the foundations of the building, build floor
# 2. create corner pillars
# 3. between each pair of pillars, use Cellular Automata to build a wall
# 4. create celing at the ceiling level
def buildStructure(level, box):
	floor = makeFloorPlan(level, box)
	buildingHeightInfo = createPillars(level, floor)
	generateWalls(level, floor, buildingHeightInfo)
	generateCeiling(level, floor, buildingHeightInfo)

def makeFloorPlan(level, box):
	# we have to first figure out where in the box this is going to be
	# find the box dimensions
	(width, height, depth) = getBoxSize(box)

	# get eights
	fractionWidth = width / 4
	fractionDepth = depth / 4
	print (fractionWidth)
	print (fractionDepth)
	# create the box boundaries
	xstart = box.minx + random.randint(0, fractionWidth) + 1
	zstart = box.minz + random.randint(0, fractionDepth) + 1

	xsize = width - random.randint(0, fractionWidth) - 5
	zsize = depth - random.randint(0, fractionDepth) - 5

	floorplan = BoundingBox((xstart, box.miny, zstart), (xsize, box.maxy, zsize))
	return floorplan

# we need to create the corners for the walls.
#Every building needs corners for stability...unless you are inventive... :)
def createPillars(level, floor):
	cornerBlockStarts = []
	ycoords = []
	# similarly to fences, we need to countdown on each of the four corners and find the block where the ground starts, then start building pillars above that height
	midpointFloorHeight = 0
	for y in xrange(floor.maxy, floor.miny, -1):
		# get this block
		tempBlock = level.blockAt(floor.minx, y, floor.minz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.minx, y+1, floor.minz))
			break;
	for y in xrange(floor.maxy, floor.miny, -1):
		# get this block
		tempBlock = level.blockAt(floor.minx, y, floor.maxz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.minx, y+1, floor.maxz))
			break;
	for y in xrange(floor.maxy, floor.miny, -1):
		# get this block
		tempBlock = level.blockAt(floor.maxx, y, floor.minz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.maxx, y+1, floor.minz))
			break;
	for y in xrange(floor.maxy, floor.miny, -1):
		# get this block
		tempBlock = level.blockAt(floor.maxx, y, floor.maxz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.maxx, y+1, floor.maxz))
			break;

	# now we have all four corners. for each, pick a random y value between 5 and 10, and build up using stone
	ystartCoordMax = -10000
	for cornerstone in cornerBlockStarts:
		midpointFloorHeight += cornerstone[1]
		if(cornerstone[1] > ystartCoordMax):
			ystartCoordMax = cornerstone[1]
		pillarheight = random.randint(5, 10)
		for y in range(0, pillarheight):
			setBlock(level, (4,0), cornerstone[0], cornerstone[1]+y, cornerstone[2])
			if(y==pillarheight-1):
				# add y to our y coords, which will be used to determine building height for the roof
				ycoords.append(y)
	allYs = 0
	for ycoord in ycoords:
		allYs += ycoord
	yavg = allYs / 4
	midpointFloorHeight = midpointFloorHeight / 4
	print("Average pillar height: ", yavg)
	return (yavg, ystartCoordMax, midpointFloorHeight)

# the walls of the building are generated each using independent ceullular automata. We look at the immediate neighborhood and take action
# cellular automata is done in 3 easy steps
# 1. intitialize with random block placement in the space
# 2. evaluate each cell, checking its neighbors to gauge changes
# 3. repeat 2 until satisfied
def generateWalls(level, floor, buildingHeightInfo):
	print "Generating walls"
	# actual automata is going to be simulated in a matrix (it's much faster than rendering it in minecraft)
	# first we should define the matrix properties (i.e. width and height)
	(width, boxheight, depth) = getBoxSize(floor)
	height = buildingHeightInfo[0]
	print "X walls"
	for k in range(2):
		print "i:", k
		print("matrix width: ", width, "Matrix height: ", height)
		# we have our matrix for CA, now lets do CA
		matrix = [[0 for x in range(width)] for y in range(height)]
		matrixnew = randomlyAssign(matrix, width, height)
		for j in range(height):
			for i in range(width):
				print matrixnew[j][i],
			print
		# do 3 generations
		for gen in range(0,2):
			print "Generation ", gen
			matrixnew = cellularAutomataGeneration(matrixnew, width, height)
			for j in range(height):
				for i in range(width):
					print matrixnew[j][i],
				print
		#after generation is over, place the walls according to the wall matrix, starting at the floor
		for y in range(height):
			for x in range(1,width):
				if k==1:
					print "boom 1"
					if matrixnew[y][x] == 1:
						setBlock(level, (4, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.minz)
					else:
						setBlock(level, (20, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.minz)
				else:
					print "boom 2"
					if matrixnew[y][x] == 1:
						setBlock(level, (4, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.maxz)
					else:
						setBlock(level, (20, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.maxz)
	print "Z Walls"
	for k in range(2):
		print "j:",j
		# we have our matrix for CA, now lets do CA
		matrix = [[0 for x in range(depth)] for y in range(height)]
		matrixnew = randomlyAssign(matrix, depth, height)
		print "pre cellular automata"
		for j in range(height):
			for i in range(depth):
				print matrixnew[j][i],
			print
		# do 3 generations
		for gen in range(0,2):
			print "Generation ", gen
			matrixnew = cellularAutomataGeneration(matrixnew, depth, height)
			for j in range(height):
				for i in range(depth):
					print matrixnew[j][i],
				print
		#after generation is over, place the walls according to the wall matrix, starting at the floor
		for y in range(height):
			for z in range(1,depth):
				if k==1:
					print "boom 3"
					if matrixnew[y][z] == 1:
						setBlock(level, (4, 0), floor.minx, buildingHeightInfo[2] + y, floor.minz+z)
					else:
						setBlock(level, (20, 0), floor.minx, buildingHeightInfo[2] + y, floor.minz+z)
				else:
					print "boom 4"
					if matrixnew[y][z] == 1:
						setBlock(level, (4, 0), floor.maxx, buildingHeightInfo[2] + y, floor.minz+z)
					else:
						setBlock(level, (20, 0), floor.maxx, buildingHeightInfo[2] + y, floor.minz+z)
def randomlyAssign(matrix, width, height):
	print 'randomly assigning to matrix'
	for j in range(height):
		for i in range(width):
			print j,i
			matrix[j][i] = random.randint(0,2)
	return matrix

def cellularAutomataGeneration(matrix, width, height):
	for j in range(height):
		for i in range(width):
			print j,i
			if j == 0 : #special case for bottom
				matrix[j][i] = decideCell(1, matrix[j+1][i])
			elif j == height-1 : #special case for top
				matrix[j][i] = decideCell(matrix[j-1][i], 1)
			else:
				matrix[j][i] = decideCell(matrix[j-1][i], matrix[j+1][i])
	return matrix

# the rules for cellular automata are as follows:
# look above and below me.
#	If one of my neighbors is 0, I have a 50% chance to be 0
# 	If both of my neighbors are 0, I have a 85% chance to be 1
#	If both of my neighbors are 1, I have a 50% chance to be 0
def decideCell(top, bottom):
	if top + bottom == 1:
		chance = random.randint(0, 100)
		if chance < 50:
			return 0
		else:
			return 1
	elif top + bottom == 0:
		chance = random.randint(0, 100)
		if chance < 90:
			return 1
		else:
			return 0
	elif top + bottom == 2:
		chance = random.randint(0,100)
		if chance < 20:
			return 0
		else:
			return 1
# puts a cap on the building in question
# uses the floor to determine the celing size, and the buildingHeightInfo tuple
# to place it at the right level
def generateCeiling(level, floor, buildingHeightInfo):
	print "generating ceiling"
	for x in range(floor.minx, floor.maxx+1):
		for z in range(floor.minz, floor.maxz+1):
			setBlock(level, (4, 0), x, buildingHeightInfo[2] + buildingHeightInfo[0], z)
