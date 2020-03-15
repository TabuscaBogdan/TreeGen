import bpy
import math
import random
import decimal

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
    verts =[]
    for step in range(0,nrCircleVertexes):
        theta = stepRotation * step
        x = ray * math.sin(theta)
        y = ray * math.cos(theta)
        vertex = (x,y,0)
        verts.append(vertex)
    return verts
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


def CalculateCircleFace(nrCircleVertexes,circleVertexes):
    face=(0,)
    for i in range(1,nrCircleVertexes):
        face+=(i,)
    return face

def CreateShapeOutOfCircleVertexes(nrCircleVertexes,circlesVertexes):
    nrOfVertexes = len(circlesVertexes)
    nrOfCircles = nrOfVertexes//nrCircleVertexes
    faces=[]
    for circle in range(0,nrOfCircles-1):
        for vert in range(0,nrCircleVertexes):
            if((vert+1+nrCircleVertexes*(circle+1))%nrCircleVertexes!=0):
                face = (vert + nrCircleVertexes * circle, vert + 1 + circle * nrCircleVertexes,
                        vert + 1 + nrCircleVertexes * (circle + 1), vert + nrCircleVertexes * (circle + 1))
            else:
                face = (vert + nrCircleVertexes * circle, circle * nrCircleVertexes,
                        nrCircleVertexes * (circle + 1), vert + nrCircleVertexes * (circle + 1))

            faces.append(face)
    return faces


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