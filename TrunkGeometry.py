import bpy
import bmesh
import math
import random
import mathutils
import os
utilityScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\GeneralGeometry.py"#os.path.join(os.path.dirname(os.path.abspath( __file__ )),"GeneralGeometry.py").replace("\\Scripting.blend",'')

import importlib.util
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)

branchScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\BranchGeometry.py" #os.path.join(os.path.dirname(os.path.abspath( __file__ )),"BranchGeometry.py")
branchSpec = importlib.util.spec_from_file_location("BranchGeometry", branchScriptPath)
bGeo = importlib.util.module_from_spec(branchSpec)
branchSpec.loader.exec_module(bGeo)

stumpScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\StumpGeometry.py" #os.path.join(os.path.dirname(os.path.abspath( __file__ )),"StumpGeometry.py")
stumpSpec = importlib.util.spec_from_file_location("StumpGeometry", stumpScriptPath)
sGeo = importlib.util.module_from_spec(stumpSpec)
stumpSpec.loader.exec_module(sGeo)

verts = []
faces = []
edges = []

def DetermineZAngleInterval(initialAngles, anglesIntervals):
    zAngle = initialAngles[0]
    oldInterval = anglesIntervals[0]

    midPointAngle = (oldInterval[0]+oldInterval[1])/2

    if(zAngle>midPointAngle):
        upperAngleLimit = oldInterval[1] + zAngle - midPointAngle
        if(upperAngleLimit>maxBranchAngleDeviation):
            return anglesIntervals
        else:
            lowerAngleLimit = oldInterval[0] + zAngle - midPointAngle
            anglesIntervals[0] = [lowerAngleLimit, upperAngleLimit]
            return anglesIntervals
    else:
        lowerAngleLimit = oldInterval[0] - (midPointAngle - zAngle)
        if(lowerAngleLimit < minBranchAngleDeviation):
            return anglesIntervals
        else:
            upperAngleLimit = oldInterval[1] - (midPointAngle - zAngle)
            anglesIntervals[0] = [lowerAngleLimit, upperAngleLimit]
            return anglesIntervals




def CalculateSplitBranchThickness(nrOfbranches):
    #Most of the time there exists a main branch, when a tree splits,
    thicknessPrecents =[]

    mainBranchMaxThickness=100 #precent
    mainBranchMinThickness= int(mainBranchMaxThickness/mainBranchMinimumThicknessReductionOnSplit)

    secondaryBranchMaxThickness = 95 #precent
    secondaryBranchMinThickness = int(secondaryBranchMaxThickness/secondaryBranchMinimumThicknessReductionOnSplit)

    mainBranchRayPrecent = random.randrange(mainBranchMinThickness,mainBranchMaxThickness)
    thicknessPrecents.append(mainBranchRayPrecent)

    for i in range(1,nrOfbranches):
        secondaryBranchThickness = random.randrange(secondaryBranchMinThickness,secondaryBranchMaxThickness)
        thicknessPrecents.append(secondaryBranchThickness)

    return thicknessPrecents



def Split(currentPosition,circleNumber,anglesIntervals,sphereRayInterval,initialAngles,branchSplitNumber,currentRayPrecent):
    branchAngleSections = []
    branches = []

    anglesIntervals[1]=[0,math.pi*2]

    angleSection = anglesIntervals[1][1]/branchSplitNumber
    deadSection = anglesIntervals[1][1]/(branchSplitNumber+1)
    spinAngle = random.uniform(0,math.pi)
    #deadSection = angleSection/branchSplitNumber


    for i in range(0,branchSplitNumber):
        sectionAngleIntervals =[[anglesIntervals[0][0],anglesIntervals[0][1]],[angleSection*i+spinAngle,angleSection*(i+1)+spinAngle-deadSection]]

        branchPositionAndAngles = geo.PickPointInSemiSphere(currentPosition,sphereRayInterval,initialAngles, sectionAngleIntervals, precision)

        branches.append(branchPositionAndAngles)
        branchAngleSections.append(sectionAngleIntervals)

    branchPrecents = CalculateSplitBranchThickness(branchSplitNumber)
    for i in range(0,branchSplitNumber):

        branchPrecents[i] = int((currentRayPrecent/100)*branchPrecents[i])

        branches[i].append(branchPrecents[i])
        branches[i].append(circleNumber)

        branches[i].append(branchAngleSections[i])

    return branches

def GrowBranchingTrunk(currentPosition,shape,initialCircleNumber,isMainBranch, anglesIntervals, currentRayPrecent,rayReductionPrecentPerStep, raySphereInterval, startingSplitChance, splitChanceGain):
    bodyCilynder = []
    bodyCilynderFaces = []
    bodyCilynder.append(shape)
    global currentCircleNumber
    global splitInterval

    splitStop=0
    mainBranch=0

    while(currentRayPrecent>=stopCircleRayPrecent and splitStop==0):

        rayInterval = [(raySphereInterval[0]/100)*currentRayPrecent,(raySphereInterval[1]/100)*currentRayPrecent]
        positionAndAngles = geo.PickPointInSemiSphere(currentPosition, rayInterval=rayInterval,
                                                      initialAngles=[0, 0], anglesIntervals=anglesIntervals,
                                                      precision=precision)

        currentPosition = positionAndAngles[0]
        initialAngles = positionAndAngles[1]

        initialShape = shape

        #ThicknessProblemFix
        minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(initialShape)

        shape = geo.CalculateResizedDeformedCircle(len(shape),minDeformedCircleRay,currentRayPrecent,deformities=[])
        shape= geo.rotateCircleOnSphereAxis(shape,initialAngles)
        newShapePlacement = geo.addVectorToVerts(currentPosition, shape)

        currentRayPrecent -= rayReductionPrecentPerStep

        bodyCilynder.append(newShapePlacement)
        currentCircleNumber += 1

        bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), initialCircleNumber, currentCircleNumber))
        initialCircleNumber = currentCircleNumber

        chanceToSplit = random.randrange(0,100)
        if(chanceToSplit<=startingSplitChance):
            splitStop = 1

            numberOfSplits = random.randint(splitInterval[0],splitInterval[1])
            treeSplit = Split(currentPosition, currentCircleNumber, anglesIntervals, rayInterval, initialAngles=[0,0],
                              branchSplitNumber=numberOfSplits,currentRayPrecent = currentRayPrecent)

            for j in range(0,len(treeSplit)):
                currentPosition = treeSplit[j][0]
                initialAngles = treeSplit[j][1]

                #Thickness Problem Fix
                minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(initialShape)

                currentRayPrecent = treeSplit[j][2]
                previousCircleNumber = treeSplit[j][3]
                sectionAngles = treeSplit[j][4]

                shape = geo.CalculateResizedDeformedCircle(len(shape), minDeformedCircleRay, currentRayPrecent, deformities=[])
                shape = geo.rotateCircleOnSphereAxis(shape, initialAngles)
                newShapePlacement = geo.addVectorToVerts(currentPosition, shape)
                bodyCilynder.append(newShapePlacement)
                currentCircleNumber +=1
                bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), previousCircleNumber, currentCircleNumber))
                initialCircleNumber = currentCircleNumber

                branchIdentifier = j + isMainBranch

                if(branchIdentifier==mainBranch):
                    branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber,
                                                               branchIdentifier, anglesIntervals, currentRayPrecent,
                                                               rayReductionPrecentPerStep, raySphereInterval,
                                                               startingSplitChance, splitChanceGain)
                else:
                    deviantAnglesIntervals = DetermineZAngleInterval(initialAngles,anglesIntervals)
                    deviantAnglesIntervals[1] = sectionAngles[1]
                    branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber,
                                                               branchIdentifier, deviantAnglesIntervals, currentRayPrecent,
                                                               rayReductionPrecentPerStep, raySphereInterval,
                                                               startingSplitChance, splitChanceGain)


                bodyCilynder.extend(branchCirclesAndFaces[0])
                bodyCilynderFaces.extend(branchCirclesAndFaces[1])

        else:
            startingSplitChance+=splitChanceGain

    # remove the initial stump face
    bodyCilynder.pop(0)
    return [bodyCilynder, bodyCilynderFaces]


def GrowTrunk(iterations,currentPosition,shape,initialCircle,randomIntervalTouple,deformities,mutationChance,mutationFactor):
    bodyCilynder=[]
    bodyCilynderFaces = []
    bodyCilynder.append(shape)

    nrCircle = initialCircle

    initialAngles = [0,0]
    anglesIntervals = [[0,math.pi/6],[0,math.pi*2]]

    for i in range(1,iterations):
        positionAndAngles = geo.PickPointInSemiSphere(currentPosition, rayInterval = [2,2], initialAngles = [0,0], anglesIntervals = anglesIntervals, precision = precision)

        currentPosition = positionAndAngles[0]
        initialAngles = positionAndAngles[1]

        maxDeformedCircleRay = geo.FindMaxRayOfDeformedCircle(shape)
        minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(shape)
        #mutationInterval =[0,maxDeformedCircleRay-minDeformedCircleRay]
        #deformities = geo.MutateValues(deformities, mutationInterval, mutationFactor, mutationChance, precision=2)

        shape = geo.CalculateResizedDeformedCircle(len(shape),minDeformedCircleRay,99-i/50,deformities=[])
        shape= geo.rotateCircleOnSphereAxis(shape,initialAngles)
        newShapePlacement = geo.addVectorToVerts(currentPosition, shape)

        bodyCilynder.append(newShapePlacement)

        nrCircle += 1
        bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), initialCircle, nrCircle))
        initialCircle = nrCircle

        if(i==9):
            treeSplit=Split(currentPosition,shape,nrCircle,anglesIntervals,[3,8],initialAngles = [0,0],branchSplitNumber=5)
            for j in range(0,len(treeSplit)):
                currentPosition = treeSplit[j][0]
                initialAngles = treeSplit[j][1]
                minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(shape)
                shape = geo.CalculateResizedDeformedCircle(len(shape), minDeformedCircleRay, treeSplit[j][2], deformities=[])
                shape = geo.rotateCircleOnSphereAxis(shape, initialAngles)
                newShapePlacement = geo.addVectorToVerts(currentPosition, shape)
                bodyCilynder.append(newShapePlacement)
                nrCircle +=1
                bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), treeSplit[j][3], nrCircle))


    #remove the initial stump face
    bodyCilynder.pop(0)
    return [bodyCilynder,bodyCilynderFaces]


#==============================================================
#====Globals=====
currentCircleNumber = 0
#===Parameters===
nrCircleVertexes=60
precision = 2
circleRay=3
stumpAbruptness = 2
barkMutationChance=0.5
barkMutationFactor=4#Lower factor = more noticeable, Greater = less noticeable

#Branching
stopCircleRayPrecent = 30
rayReductionPrecentPerStep = 2
raySphereInterval = [circleRay,circleRay*2]

anglesIntervals = [[0,math.pi/4],[0,math.pi*2]]
maxBranchAngleDeviation = math.pi/1.2
minBranchAngleDeviation = -maxBranchAngleDeviation #anglesIntervals[0][0]

splitInterval = [2,3]
startingSplitChance = 10
splichanceGain = 2

mainBranchMinimumThicknessReductionOnSplit =1.1
secondaryBranchMinimumThicknessReductionOnSplit = 1.1
#================


deformities = geo.SmoothRandom((0, 2), 1, nrCircleVertexes)

#Stump============
stumpCircles = sGeo.CalculateStumpCircles(nrCircleVertexes, circleRay, deformities, stumpAbruptness, height=1, finese=0.1)

verts.extend(geo.ConvertCirclesToVerts(stumpCircles))
faces.extend(sGeo.CalculateStumpFaces(stumpCircles))
faces.append(geo.CalculateCircleFace(nrCircleVertexes,verts))
#=================

circle = stumpCircles[-1]

deformities=geo.FindCircleDeformities(circle)

lastCircleNumber=len(stumpCircles)-1
currentCircleNumber = lastCircleNumber

lastStumpCirclePosition = (0,0,circle[0][2])

#trunk = GrowTrunk(10,(0,0,circle[0][2]),circle,lastCircleNumber,(-0.2,0.2),deformities,barkMutationChance,barkMutationFactor,1)
trunk = GrowBranchingTrunk(currentPosition=lastStumpCirclePosition, shape=circle, initialCircleNumber=lastCircleNumber,
                           isMainBranch= 0, anglesIntervals= anglesIntervals,currentRayPrecent=100,rayReductionPrecentPerStep=rayReductionPrecentPerStep,
                           raySphereInterval= raySphereInterval,startingSplitChance= startingSplitChance, splitChanceGain= splichanceGain)

for tCircle in trunk[0]:
    verts.extend(tCircle)

#=======================
faces.extend(trunk[1])
# create mesh and object
mymesh = bpy.data.meshes.new("myshape")
myobject = bpy.data.objects.new("myshape", mymesh)

# set mesh location
myobject.location = (0, 0, 0)
scene = bpy.context.scene
scene.collection.objects.link(myobject)

# create mesh from python data
mymesh.from_pydata(verts, edges, faces)
mymesh.update(calc_edges=True)

