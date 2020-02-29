import bpy
import math
import random
import decimal


# mesh arrays
#conteaza ordinea
#(x,z,y) desi in blender axele sunt puse ca si (x,y,z)
verts = []
faces = []
edges = []
#=============================== General Utility ======================================
def SmoothRandom(bigInterval, littleIntervalSize, valuesNeeded, precision=1):
    if(bigInterval[0]>=bigInterval[1]):
        raise ValueError("Not a valid interval given")
    if(bigInterval[1]-bigInterval[0]<littleIntervalSize):
        raise ValueError("Little interval size is too large")

    pivot = round(random.uniform(bigInterval[0]+littleIntervalSize/2,bigInterval[1]-littleIntervalSize/2),precision)
    nr=0
    smoothRandomNumbers=[]
    while nr<valuesNeeded:
        nr+=1
        rngNumber= round(random.uniform(pivot-littleIntervalSize/2,pivot+littleIntervalSize/2),precision)
        smoothRandomNumbers.append(rngNumber)
        if((rngNumber+littleIntervalSize/2)<=bigInterval[1] and (rngNumber-littleIntervalSize/2)>=bigInterval[0]):
            pivot=rngNumber

    return smoothRandomNumbers

def replace_at_index1(tup, ix, val):
    lst = list(tup)
    lst[ix] = val
    return tuple(lst)

def drange(x, y, jump):
    if(x<y):
        while x <= y:
            yield float(x)
            x += decimal.Decimal(jump)
    else:
        while x >= y:
            yield float(x)
            x -= decimal.Decimal(jump)

def CalculateVertexCircle(nrCircleVertexes,ray):
    fullRotation = math.pi*2
    stepRotation = fullRotation/nrCircleVertexes

    for step in range(0,nrCircleVertexes):
        theta = stepRotation * step
        x = ray * math.sin(theta)
        y = ray * math.cos(theta)
        vertex = (x,y,0)
        verts.append(vertex)
#=========================================================================================


def CalculateVertexDeformedCircle(nrCircleVertexes, ray, deformities):
    fullRotation = math.pi * 2
    stepRotation = fullRotation / nrCircleVertexes
    circleVerts=[]

    for step in range(0, nrCircleVertexes):
        theta = stepRotation * step
        x = (deformities[step] + ray) * math.sin(theta)
        y = (deformities[step] + ray) * math.cos(theta)
        vertex = (x, y, 0)
        circleVerts.append(vertex)
    return circleVerts


def CalculateCircleFace(nrCircleVertexes):
    face=(0,)
    for i in range(1,nrCircleVertexes):
        face+=(i,)
    faces.append(face)

def CreateShapeOutOfCircleVertexes(nrCircleVertexes):
    nrOfVertexes = len(verts)
    nrOfCircles = nrOfVertexes//nrCircleVertexes

    for circle in range(0,nrOfCircles-1):
        for vert in range(0,nrCircleVertexes):
            if((vert+1+nrCircleVertexes*(circle+1))%nrCircleVertexes!=0):
                face = (vert + nrCircleVertexes * circle, vert + 1 + circle * nrCircleVertexes,
                        vert + 1 + nrCircleVertexes * (circle + 1), vert + nrCircleVertexes * (circle + 1))
            else:
                face = (vert + nrCircleVertexes * circle, circle * nrCircleVertexes,
                        nrCircleVertexes * (circle + 1), vert + nrCircleVertexes * (circle + 1))

            faces.append(face)


#==================== Size =====================================

def CalculateResizedDeformedCircle(nrCircleVertexes,ray,precent,deformities=[]):
    circleVertexes = []
    fullRotation = math.pi * 2
    stepRotation = fullRotation / nrCircleVertexes

    for step in range(0, nrCircleVertexes):
        theta = stepRotation * step
        if(deformities!=[]):
            x = (((deformities[step] + ray) * precent) / 100) * math.sin(theta)
            y = (((deformities[step] + ray) * precent) / 100) * math.cos(theta)
        else:
            x = ((ray * precent) / 100) * math.sin(theta)
            y = ((ray * precent) / 100) * math.cos(theta)

        vertex = (x, y, 0)
        circleVertexes.append(vertex)
    return circleVertexes

#=============== Tree Stump Geometry ================================
lastLowerStumpCirclePrecent = 100

#Uses logarthim to generate curve
#Sets lastLowerStumpCirclePrecent
def CalculateLowerStump(nrCircleVertexes,ray,deformities,finese=0.1):
    logCurveStart = 3
    logCurveStop = 2

    stumpLowerCircles=[]
    precents =[]
    for x in drange(logCurveStart, logCurveStop, finese):
        reducedCirclePrecent = 100 * (-math.log(x)) / -math.log(logCurveStart)
        precents.append(reducedCirclePrecent)

    global lastLowerStumpCirclePrecent
    nrCircles = 0
    for circlePrecent in precents:
        resizedCircle= CalculateResizedDeformedCircle(nrCircleVertexes, ray, circlePrecent, deformities)
        lastLowerStumpCirclePrecent = circlePrecent
        for resizedVertexNr in range(0,nrCircleVertexes):
            resizedCircle[resizedVertexNr]=replace_at_index1(resizedCircle[resizedVertexNr],2,resizedCircle[resizedVertexNr][2]+nrCircles*finese)
        nrCircles+=1

        stumpLowerCircles.append(resizedCircle)
    return stumpLowerCircles

#Warning: uses lastLowerStumpCirclePrecent global Variable
def CalculateUpperStump(nrCircleVertexes,ray,deformities,lastLowerStumpCircle,abruptness=2,height=1,finese=0.1):
    logCurveLowerStump = 3
    logCurveStart = 2
    logCurveStop = 1.5

    precents =[]
    for x in drange(logCurveStart, logCurveStop, finese/2):
        reducedCirclePrecent = 100 * (-math.log(x)) / -math.log(logCurveLowerStump)
        precents.append(reducedCirclePrecent)


    maxRay=max(deformities)
    minRay=min(deformities)
    nrOfSmoothSteps=int(height/finese)
    heightStep=height/nrOfSmoothSteps
    rayReduction=(maxRay-minRay)/(nrOfSmoothSteps)
    noise = random.randrange(1,3,1)
    smoothDeformities=deformities.copy()

    smoothCircles =[]

    for step in range(0,nrOfSmoothSteps-noise):
        for i in range(0,nrCircleVertexes):
            if(smoothDeformities[i]>(maxRay-step*rayReduction)):
                smoothDeformities[i]=maxRay-step*rayReduction
        smoothCircle = CalculateResizedDeformedCircle(nrCircleVertexes,ray,precents[step],smoothDeformities)
        for i in range(0,nrCircleVertexes):
            smoothCircle[i] = replace_at_index1(smoothCircle[i],2,lastLowerStumpCircle[i][2]+(heightStep*(step+1))*abruptness)
        smoothCircles.append(smoothCircle)

    return smoothCircles




def CalculateStump(nrCircleVertexes,ray,deformities,abruptness,height,finese=0.1):
    stumpVertexes = []

    lowerStumpCircles = CalculateLowerStump(nrCircleVertexes,ray,deformities,finese)
    upperStumpCircles = CalculateUpperStump(nrCircleVertexes,ray,deformities,lowerStumpCircles[-1],abruptness,height,finese)
    for circle in lowerStumpCircles:
        stumpVertexes.extend(circle)
    for circle in upperStumpCircles:
        stumpVertexes.extend(circle)

    return stumpVertexes

#===============================================================
#===Parameters===
nrCircleVertexes=60
circleRay=2
stumpAbruptness = 2
#================

deformities = SmoothRandom((0, 2), 1, nrCircleVertexes)
verts.extend(CalculateStump(nrCircleVertexes,circleRay,deformities,stumpAbruptness,height=1,finese=0.1))

CreateShapeOutOfCircleVertexes(nrCircleVertexes)
CalculateCircleFace(nrCircleVertexes)
# create mesh and object
mymesh = bpy.data.meshes.new("myshape")
myobject = bpy.data.objects.new("myshape", mymesh)

# set mesh location
myobject.location = (0,0,0)
scene =bpy.context.scene
scene.collection.objects.link(myobject)

# create mesh from python data
mymesh.from_pydata(verts, edges, faces)
mymesh.update(calc_edges=True)




