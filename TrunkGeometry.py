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
treeObjects = []


def DeformitiesCheck(deformities,initialShape,minDeformedCircleRay):
    if (deformities != []):
        maxDeformedCircleRay = geo.FindMaxRayOfDeformedCircle(initialShape)
        mutationInterval = [0, maxDeformedCircleRay - minDeformedCircleRay]
        deformities = geo.MutateValues(deformities, mutationInterval, barkMutationFactor, barkMutationChance,
                                       precision=2)
        return deformities
    return []

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

def JoinTreeObjectsWithTree(tree):
    global treeObjects
    #join leaf with Trunk
    tree.select_set(True)
    bpy.context.view_layer.objects.active = tree
    for treeObject in treeObjects:
        treeObject.select_set(True)

    bpy.ops.object.join()
    bpy.ops.object.select_all(action='DESELECT')
    treeObjects = []

def AddLeaf(angles, extraRotation, endPoint, scene, sourceObject):
    xRot=extraRotation[0]
    yRot=extraRotation[1]
    zRot=extraRotation[2]

    global treeObjects

    newObject = sourceObject.copy()
    newObject.data = sourceObject.data.copy()
    newObject.location = endPoint
    eulerAngles = geo.getEulerAnglesFromSphereAngles(angles)
    #newObject.rotation_euler = (eulerAngles[0]+xRot, eulerAngles[1]+yRot, eulerAngles[2]+zRot)
    newObject.rotation_euler = (xRot, yRot, eulerAngles[2] + zRot)
    # newObject.parent = parentObject
    scene.collection.objects.link(newObject)
    treeObjects.append(newObject)


def GrowLeaves(leafSegments,TreeMeshName,LeafMeshName,hasEndingLeaf=1):
    scene = bpy.context.scene
    sourceObject = bpy.data.objects[LeafMeshName]
    parentObject = bpy.data.objects[TreeMeshName]

    for segment in leafSegments:

        startPoint = segment[0]
        angles = segment[1]
        endPoint = segment[2]
        distance = geo.CalculateDistanceBetweenTwoPoints(startPoint,endPoint)

        deviation = random.randint(0, 360)
        zLeafRotation = (math.pi / 180) * deviation
        xLeafRotation, yLeafRotation = WindDeviation()
        extraRotation = [xLeafRotation, yLeafRotation, zLeafRotation]

        if(hasEndingLeaf!=0):
            AddLeaf(angles, extraRotation , endPoint, scene, sourceObject)

        leafNumber = random.randint(leavesPerBranch[0],leavesPerBranch[1])
        unitDistance = (distance/leavesPerBranch[1])/leavesDistance
        position = endPoint
        for i in range(0,leafNumber):
            if(i%2==1):
                leafDistance = (distance-(unitDistance * i))/distance
                x = startPoint[0]+leafDistance*(endPoint[0]-startPoint[0])
                y = startPoint[1] + leafDistance * (endPoint[1] - startPoint[1])
                z = startPoint[2] + leafDistance * (endPoint[2] - startPoint[2])
                position = tuple([x,y,z])

                deviation = random.randint(leafRotationAngleDeviation[0],leafRotationAngleDeviation[1])
                zLeafRotation =(math.pi/180)*90+(math.pi/180)*deviation +extraRotation[2]
                xLeafRotation, yLeafRotation = WindDeviation()
                secondaryRotations = [xLeafRotation, yLeafRotation, zLeafRotation]

                AddLeaf(angles, secondaryRotations, position, scene, sourceObject)
            else:
                deviation = random.randint(leafRotationAngleDeviation[0], leafRotationAngleDeviation[1])
                zLeafRotation = math.pi + (math.pi / 180) * deviation+extraRotation[2]
                xLeafRotation, yLeafRotation = WindDeviation()
                secondaryRotations = [xLeafRotation, yLeafRotation, zLeafRotation]
                AddLeaf(angles, secondaryRotations, position, scene, sourceObject)


def WindDeviation():
    minorDeviation = random.randint(int(leafRotationAngleDeviation[0] / 2), int(leafRotationAngleDeviation[1] / 2))
    yLeafRotation = (math.pi / 180) * minorDeviation
    minorDeviation = random.randint(int(leafRotationAngleDeviation[0] / 2), int(leafRotationAngleDeviation[1] / 2))
    xLeafRotation = (math.pi / 180) * minorDeviation
    return xLeafRotation, yLeafRotation


def GrowBranchingTrunk(currentPosition,shape,initialCircleNumber,previousPosition,oldAngles,isMainBranch, anglesIntervals, currentRayPrecent,rayReductionPrecentPerStep, raySphereInterval, startingSplitChance, splitChanceGain, deformities):
    bodyCilynder = []
    bodyCilynderFaces = []
    leafSegments = []
    bodyCilynder.append(shape)
    global currentCircleNumber
    global splitInterval

    splitStop=0
    mainBranch=0

    if(currentRayPrecent<stopCircleRayPrecent):
        leafSegment =[previousPosition,oldAngles,currentPosition]
        leafSegments.append(leafSegment)

    while(currentRayPrecent>=stopCircleRayPrecent and splitStop==0):

        previousPosition = currentPosition
        rayInterval = [(raySphereInterval[0]/100)*currentRayPrecent,(raySphereInterval[1]/100)*currentRayPrecent]
        positionAndAngles = geo.PickPointInSemiSphere(currentPosition, rayInterval=rayInterval,
                                                      initialAngles=[0, 0], anglesIntervals=anglesIntervals,
                                                      precision=precision)

        currentPosition = positionAndAngles[0]
        initialAngles = positionAndAngles[1]

        initialShape = shape

        #ThicknessProblemFix
        minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(initialShape)

        deformities = DeformitiesCheck(deformities,initialShape,minDeformedCircleRay)

        shape = geo.CalculateResizedDeformedCircle(len(shape),minDeformedCircleRay,currentRayPrecent,deformities=deformities)
        shape = geo.rotateCircleOnSphereAxis(shape,initialAngles)
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
            previousPosition = currentPosition

            for j in range(0,len(treeSplit)):
                currentPosition = treeSplit[j][0]
                initialAngles = treeSplit[j][1]

                #Thickness Problem Fix
                minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(initialShape)

                deformities = DeformitiesCheck(deformities, initialShape, minDeformedCircleRay)

                currentRayPrecent = treeSplit[j][2]
                previousCircleNumber = treeSplit[j][3]
                sectionAngles = treeSplit[j][4]

                shape = geo.CalculateResizedDeformedCircle(len(shape), minDeformedCircleRay, currentRayPrecent, deformities=deformities)
                shape = geo.rotateCircleOnSphereAxis(shape, initialAngles)
                newShapePlacement = geo.addVectorToVerts(currentPosition, shape)
                bodyCilynder.append(newShapePlacement)
                currentCircleNumber +=1
                bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), previousCircleNumber, currentCircleNumber))
                initialCircleNumber = currentCircleNumber

                branchIdentifier = j + isMainBranch

                if(branchIdentifier==mainBranch):
                    branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber, previousPosition, initialAngles,
                                                               branchIdentifier, anglesIntervals, currentRayPrecent,
                                                               rayReductionPrecentPerStep, raySphereInterval,
                                                               startingSplitChance, splitChanceGain, deformities)
                else:
                    deviantAnglesIntervals = DetermineZAngleInterval(initialAngles,anglesIntervals)
                    deviantAnglesIntervals[1] = sectionAngles[1]
                    branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber, previousPosition, initialAngles,
                                                               branchIdentifier, deviantAnglesIntervals, currentRayPrecent,
                                                               rayReductionPrecentPerStep, raySphereInterval,
                                                               startingSplitChance, splitChanceGain, deformities)


                bodyCilynder.extend(branchCirclesAndFaces[0])
                bodyCilynderFaces.extend(branchCirclesAndFaces[1])
                leafSegments.extend(branchCirclesAndFaces[2])

        else:
            startingSplitChance+=splitChanceGain
            if (currentRayPrecent < stopCircleRayPrecent):
                leafSegment = [previousPosition, oldAngles, currentPosition]
                leafSegments.append(leafSegment)

    # remove the initial stump face
    bodyCilynder.pop(0)
    return [bodyCilynder, bodyCilynderFaces, leafSegments]


#==============================================================
def SetTreeProperties(TreeGeneralProp,TreeBarkProp,TreeBranchingProp,TreeLeavesProp):
    #===General===
    global nrCircleVertexes, precision, circleRay, stumpAbruptness
    nrCircleVertexes = TreeGeneralProp.nrCircleVertices
    circleRay = TreeGeneralProp.circleRay
    stumpAbruptness = TreeGeneralProp.stumpAbruptness
    precision = TreeGeneralProp.precision
    #============
    #===Bark===
    global enableBark, barkMutationChance, barkMutationFactor, barkMaterialName
    enableBark = TreeBarkProp.barkDeformities
    barkMutationChance = TreeBarkProp.barkMutationChance
    barkMutationFactor = TreeBarkProp.barkMutationFactor
    barkMaterialName = TreeBarkProp.barkMaterialName
    #==========
    #===Branching===
    global stopCircleRayPrecent, rayReductionPrecentPerStep, raySphereInterval
    global anglesIntervals, maxBranchAngleDeviation, minBranchAngleDeviation
    global splitInterval, startingSplitChance, splichanceGain
    stopCircleRayPrecent = TreeBranchingProp.stopCircleRayPrecent
    rayReductionPrecentPerStep = TreeBranchingProp.rayReductionPrecentPerStep
    raySphereInterval = [circleRay, circleRay*2]
    anglesIntervals = [[-math.pi/TreeBranchingProp.angleIntervalDiv, math.pi/TreeBranchingProp.angleIntervalDiv], [0, math.pi*2]]
    maxBranchAngleDeviation = math.pi/TreeBranchingProp.maxBranchingAngleDeviationDiv
    minBranchAngleDeviation = -maxBranchAngleDeviation
    splitInterval = [TreeBranchingProp.splitIntervalMinim, TreeBranchingProp.splitIntervalMaxim]
    startingSplitChance = TreeBranchingProp.startingSplitChance
    splichanceGain = TreeBranchingProp.splitChanceGain
    #==============
    #===Leaves===
    global leavesPerBranch, leavesDistance, leafRotationAngleDeviation, leafObjectName
    leavesPerBranch = [TreeLeavesProp.leavesPerBranchInferiorLimit, TreeLeavesProp.leavesPerBranchSuperiorLimit]
    leavesDistance = TreeLeavesProp.leavesDistance
    leafObjectName = TreeLeavesProp.leafObjectName
    leafRotationAngleDeviation = [-TreeLeavesProp.leafRotationAngleDeviationFactor, TreeLeavesProp.leafRotationAngleDeviationFactor]

def CreateTree():
    verts = []
    faces = []
    deformities = geo.SmoothRandom((0, 2), 1, nrCircleVertexes)
    # Stump============
    stumpCircles = sGeo.CalculateStumpCircles(nrCircleVertexes, circleRay, deformities, stumpAbruptness, height=1,
                                              finese=0.1)

    verts.extend(geo.ConvertCirclesToVerts(stumpCircles))
    faces.extend(sGeo.CalculateStumpFaces(stumpCircles))
    faces.append(geo.CalculateCircleFace(nrCircleVertexes, verts))
    circle = stumpCircles[-1]

    deformities = geo.FindCircleDeformities(circle)

    global currentCircleNumber
    lastCircleNumber = len(stumpCircles) - 1
    currentCircleNumber = lastCircleNumber

    lastStumpCirclePosition = (0, 0, circle[0][2])

    if enableBark == False:
        deformities = []

    trunk = GrowBranchingTrunk(currentPosition=lastStumpCirclePosition, shape=circle,
                               initialCircleNumber=lastCircleNumber, previousPosition=lastStumpCirclePosition,
                               oldAngles=[0, 0],
                               isMainBranch=0, anglesIntervals=anglesIntervals, currentRayPrecent=100,
                               rayReductionPrecentPerStep=rayReductionPrecentPerStep,
                               raySphereInterval=raySphereInterval, startingSplitChance=startingSplitChance,
                               splitChanceGain=splichanceGain, deformities=deformities)

    leafSegments = trunk[2]

    for tCircle in trunk[0]:
        verts.extend(tCircle)
    faces.extend(trunk[1])

    # create mesh and object
    mymesh = bpy.data.meshes.new("Tree")
    myobject = bpy.data.objects.new("Tree", mymesh)
    # assign material
    mat = bpy.data.materials.get(barkMaterialName)
    myobject.data.materials.append(mat)
    # set mesh location
    myobject.location = (0, 0, 0)
    scene = bpy.context.scene
    scene.collection.objects.link(myobject)

    mymesh.from_pydata(verts, edges, faces)
    mymesh.update(calc_edges=True)

    GrowLeaves(leafSegments, "Tree", leafObjectName)
    JoinTreeObjectsWithTree(myobject)


#====Globals=====
currentCircleNumber = 0
#===Parameters===
nrCircleVertexes=30
precision = 2
circleRay=3
stumpAbruptness = 3

#Bark
enableBark = False
barkMutationChance = 0.5
barkMutationFactor = 4  #Lower factor = more noticeable, Greater = less noticeable

#Branching
stopCircleRayPrecent = 30
rayReductionPrecentPerStep = 2
raySphereInterval = [circleRay,circleRay*2]

anglesIntervals = [[-math.pi/5,math.pi/5],[0,math.pi*2]]
maxBranchAngleDeviation = math.pi/1.2
minBranchAngleDeviation = -maxBranchAngleDeviation #anglesIntervals[0][0]

splitInterval = [2,3]
startingSplitChance = 20
splichanceGain = 1

mainBranchMinimumThicknessReductionOnSplit =1.1
secondaryBranchMinimumThicknessReductionOnSplit = 1.1
#Leaves
leavesPerBranch = [5,10]
leavesDistance = 1# greater number = smaller distance between leaves
leafRotationAngleDeviation = [-30,30]
#Materials
barkMaterialName = "Clay"
#Objects
leafObjectName = "Leaf"
#================

CreateTree()



