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

def sum_touples(tup1,tup2):
    lst1 = list(tup1)
    lst2 = list(tup2)
    sumList = []
    for i in range(0,len(lst1)):
        sumList.append(lst1[i]+lst2[i])
    return tuple(sumList)

def addVectorToVerts(toupleVector,touplesVertsList):
    new_verts = []
    for x in touplesVertsList:
        new_verts.append(sum_touples(toupleVector,x))
    return new_verts

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
        if(deformities!=[]):
            x = (deformities[step] + ray) * math.sin(theta)
            y = (deformities[step] + ray) * math.cos(theta)
        else:
            x = ray * math.sin(theta)
            y = ray * math.cos(theta)
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

def CreateFaceBetweenTwoCircles(nrCircleVertexes,firstCircle,secondCircle):
    faces =[]
    for vertexNumber in range(0,nrCircleVertexes):
        if(vertexNumber+1!=nrCircleVertexes):
            face=(vertexNumber+nrCircleVertexes*firstCircle, vertexNumber+1+nrCircleVertexes*firstCircle,
                  vertexNumber + 1 + nrCircleVertexes * secondCircle, vertexNumber+nrCircleVertexes*secondCircle)
        else:
            face=(vertexNumber+nrCircleVertexes*firstCircle, nrCircleVertexes*firstCircle,
                  nrCircleVertexes * secondCircle, vertexNumber+nrCircleVertexes*secondCircle)
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

def translateVertices(nrCircleVertexes,circleVertexes,vector,unit=1):
    movedVertices=[]
    for i in range(0, nrCircleVertexes):
        x=circleVertexes[i][0] + vector[0]*unit
        y=circleVertexes[i][1] + vector[1]*unit
        z=circleVertexes[i][2] + vector[2]*unit
        movedVertices.append((x, y, z))
    return movedVertices

#rotation
matrix_world = (((1.0, 0.0, 0.0, 0.0),
                     (0.0, 1.0, 0.0, 0.0),
                     (0.0, 0.0, 1.0, 0.0),
                     (0.0, 0.0, 0.0, 1.0)))


def matmult(X, Y):
    result = []
    for i in range(len(X)):
        result.append([])
        for j in range(len(Y[0])):
            result[i].append(0)
            for k in range(len(Y)):
                result[i][j] += X[i][k] * Y[k][j]
    return result

def rotate(nrCircleVertexes,circleVertexes,rotationMatrix):
    movedVertices = []
    for i in range(0,nrCircleVertexes):
        vectorVertice=[[circleVertexes[i][0]],[circleVertexes[i][1]],[circleVertexes[i][2]]]
        rotatedVertice=matmult(rotationMatrix,vectorVertice)
        rotatedVertice=(rotatedVertice[0][0],rotatedVertice[1][0],rotatedVertice[2][0])
        movedVertices.append(rotatedVertice)
    return movedVertices

def rotateVerticesOnX(nrCircleVertexes,circleVertexes,angleRads):
    rotationMatrixX=[[1,0,0],[0,math.cos(angleRads),-math.sin(angleRads)],[0,math.sin(angleRads),math.cos(angleRads)]]
    return rotate(nrCircleVertexes,circleVertexes,rotationMatrixX)

def rotateVerticesOnY(nrCircleVertexes,circleVertexes,angleRads):
    rotationMatrixY=[[math.cos(angleRads),0,math.sin(angleRads)],[0,1,0],[-math.sin(angleRads),0,math.cos(angleRads)]]
    return rotate(nrCircleVertexes, circleVertexes, rotationMatrixY)

def rotateVerticesOnZ(nrCircleVertexes,circleVertexes,angleRads):
    movedVertices=[]
    rotationMatrixZ=[[math.cos(angleRads),-math.sin(angleRads),0],[math.sin(angleRads),math.cos(angleRads),0],[0,0,1]]
    return rotate(nrCircleVertexes, circleVertexes, rotationMatrixZ)