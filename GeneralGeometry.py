import bpy
import math
import random
import decimal

#=============================== General Utility ======================================

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

def mul_touples(tup1,tup2):
    lst1 = list(tup1)
    lst2 = list(tup2)
    mulList = []
    for i in range(0,len(lst1)):
        mulList.append(lst1[i]*lst2[i])
    return tuple(mulList)

def div_touples(tup1,tup2):
    lst1 = list(tup1)
    lst2 = list(tup2)
    divList = []
    for i in range(0,len(lst1)):
        divList.append(lst1[i]/lst2[i])
    return tuple(divList)

def dotProd_touple(tup1,tup2):
    lst1 = list(tup1)
    lst2= list(tup2)
    value=0
    for i in range(0,len(lst1)):
        value+=lst1[i]*lst2[i]
    return value

def magnitude_touple(tup):
    value=0
    for i in range(0,len(tup)):
        value+=tup[i]**2
    return math.sqrt(value)

def mul_tuples_w_value(tup,value):
    listTuple = list(tup)
    for i in range(0,len(listTuple)):
        listTuple[i]= listTuple[i]* value;
    return tuple(listTuple)


def addVectorToVerts(toupleVector,touplesVertsList):
    new_verts = []
    for x in touplesVertsList:
        new_verts.append(sum_touples(toupleVector,x))
    return new_verts

def addVectorToVertsOnlyXY(toupleVector, toupleVertsList):
    new_verts = []
    lstVect = list(toupleVector)

    for x in toupleVertsList:
        lstVert = list(x)
        sumXYList=[]
        sumXYList.append(lstVect[0] + lstVert[0])
        sumXYList.append( lstVect[1] + lstVert[1])
        for i in range(2,len(lstVert)):
            sumXYList.append(lstVect[i])
        new_verts.append(tuple(sumXYList))
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

def ConvertCirclesToVerts(circles):
    verts=[]
    for circle in circles:
        verts.extend(circle)
    return verts


#======================================Findings==================================================
def FindMaxRayOfDeformedCircle(deformedCircle):
    circleLength = len(deformedCircle)
    halfLength = int(circleLength/2)

    maximum = CalculateDistanceBetweenTwoPoints(deformedCircle[0],deformedCircle[halfLength])
    for i in range(1,halfLength):
        distance = CalculateDistanceBetweenTwoPoints(deformedCircle[i],deformedCircle[i+halfLength])
        if(distance>maximum):
            maximum=distance
    return maximum/2

def FindMinRayOfDeformedCircle(deformedCircle):
    circleLength = len(deformedCircle)
    halfLength = int(circleLength/2)

    maxRay = FindMaxRayOfDeformedCircle(deformedCircle)
    minimum = CalculateDistanceBetweenTwoPoints(deformedCircle[0],deformedCircle[halfLength])
    for i in range(1,halfLength):
        distance = CalculateDistanceBetweenTwoPoints(deformedCircle[i],deformedCircle[i+halfLength])
        if(distance<minimum):
            minimum=distance
    minRay = maxRay-(maxRay-minimum/2)
    return minRay

def FindCircleCenter(deformedCircle):
    circleLength=len(deformedCircle)
    halfLength = int(circleLength / 2)

    maximumRay=FindMaxRayOfDeformedCircle(deformedCircle)

    for i in range(1,halfLength):
        distance = CalculateDistanceBetweenTwoPoints(deformedCircle[i],deformedCircle[i+halfLength])
        if(distance==maximumRay*2):
            centerX=(deformedCircle[i][0]+deformedCircle[i+halfLength][0]) / 2
            centerY = (deformedCircle[i][1] + deformedCircle[i + halfLength][1]) / 2
            centerZ = (deformedCircle[i][2] + deformedCircle[i + halfLength][2]) / 2
            return tuple([centerX,centerY,centerZ])

def FindCircleDeformities(deformedCircle):
    circleLength=len(deformedCircle)

    deformities=[]

    center = FindCircleCenter(deformedCircle)
    minRay = FindMinRayOfDeformedCircle(deformedCircle)

    for i in range(0,circleLength):
        distance = CalculateDistanceBetweenTwoPoints(center,deformedCircle[i])
        deformities.append(distance-minRay)
    return deformities



#======================================Calculations==============================================

def CalculateDistanceBetweenTwoPoints(Point1,Point2):
    xdistance=(Point1[0]-Point2[0])**2
    ydistance=(Point1[1]-Point2[1])**2
    zdistance=(Point1[2]-Point2[2])**2
    return math.sqrt(xdistance+ydistance+zdistance)

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
    for circle in range(0,nrOfCircles):
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


#=========================Rotations============================================================

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

def rotateCircleOnAxis(circle,axis,angle):
    circleLength= len(circle)
    movedVertices = []

    x0=axis[0]
    y0=axis[1]
    z0=axis[2]

    for vertex in circle:
        x=vertex[0]
        y=vertex[1]
        z=vertex[2]

        xRot= (x*y0-y*x0)*(1-math.cos(angle))*y0+x*math.cos(angle)
        yRot= -(x*y0-y*x0)*(1-math.cos(angle))*x0 + y*math.cos(angle)
        zRot= (x*x0+y*y0)*math.sin(angle)

        movedVertices.append(tuple([xRot,yRot,zRot]))
    return movedVertices

def rotateCircleOnSphereAxis(circle,angles):
    theta=angles[0]
    sigma=angles[1]
    rotationMatrixOnAxis =[[math.cos(theta)+(1-math.cos(theta))*(math.sin(sigma)**2), -(1-math.cos(theta))*math.sin(sigma)*math.cos(sigma), math.sin(sigma)*math.cos(sigma)],
                           [-(1-math.cos(theta))*math.sin(sigma)*math.cos(sigma), math.cos(theta)+(1-math.cos(theta))*(math.cos(theta)**2), math.sin(theta)*math.sin(sigma)],
                           [-math.sin(theta)*math.cos(sigma), -math.sin(theta)*math.sin(sigma), math.cos(theta)]
                           ]
    return rotate(len(circle),circle,rotationMatrixOnAxis)

#==============================Noise==========================================================

def AddDirectionNoiseXY(position,tupleRayInterval,intervalDecimalNumber=1):
    randomDegree = ((math.pi*2)/360)*random.randrange(0,360,1)
    randomUnit = round(random.uniform(tupleRayInterval[0],tupleRayInterval[1]), intervalDecimalNumber)

    newX = position[0]+randomUnit*math.sin(randomDegree)
    newY = position[1]+randomUnit*math.cos(randomDegree)

    return [tuple([newX,newY,position[2]]),randomDegree,randomUnit]

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

#greater mutetionFactor means less noticeable mutations (always int>0)
def MutateValues(values,mutationInterval,mutationFactor,mutationChance=0.5,precision=2):
    nrValues = len(values)

    for i in range(0,nrValues):
        chance= round(random.uniform(0,1), 1)
        if(chance>mutationChance):
            maximumMutation = (mutationInterval[1]-mutationInterval[0])/mutationFactor
            mutation = round(random.uniform(0,maximumMutation),precision)

            signChance = random.choice([-1,1])
            mutation = signChance*mutation

            if(mutation+values[i]>=mutationInterval[0] and mutation+values[i]<=mutationInterval[1]):
                values[i]+=mutation
            else:
                values[i]=mutation
    return values

#=================================Picks=======================================

def PickPointInSemiSphere(startingPosition, rayInterval, initialAngles, anglesIntervals, precision=2):
    x0 = startingPosition[0]
    y0 = startingPosition[1]
    z0 = startingPosition[2]

    ray = round(random.uniform(rayInterval[0],rayInterval[1]), precision)

    theta= random.uniform(anglesIntervals[0][0], anglesIntervals[0][1]) + initialAngles[0]
    sigma= random.uniform(anglesIntervals[1][0]/2, anglesIntervals[1][1]/2) + initialAngles[1] #for semisphere



    x= x0+ ray* math.sin(theta)*math.cos(sigma)
    y= y0+ ray* math.sin(theta)*math.sin(sigma)
    z= z0+ ray* math.cos(theta)

    return [tuple([x,y,z]),[theta,sigma]]



