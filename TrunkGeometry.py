import bpy
import math
import random
import gc

#comment in blender
# import GeneralGeometry as geo
# import StumpGeometry as sGeo
# import SegmentGeometry as tsGeo
#=================
# comment in debug
utilityScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\GeneralGeometry.py"

import importlib.util
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)

stumpScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\StumpGeometry.py"
stumpSpec = importlib.util.spec_from_file_location("StumpGeometry", stumpScriptPath)
sGeo = importlib.util.module_from_spec(stumpSpec)
stumpSpec.loader.exec_module(sGeo)

segmentScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\SegmentGeometry.py"
segmentSpec = importlib.util.spec_from_file_location("SegmentGeometry", segmentScriptPath)
tsGeo = importlib.util.module_from_spec(segmentSpec)
segmentSpec.loader.exec_module(tsGeo)

#=================

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




def PlaceNewShape(currentPosition, deformities, initialAngles, initialShape, newRayPrecent, taperedRay):
    shape = geo.CalculateResizedDeformedCircle(len(initialShape), taperedRay, newRayPrecent,
                                               deformities=deformities)
    shape = geo.rotateCircleOnSphereAxis(shape, initialAngles)
    newShapePlacement = geo.addVectorToVerts(currentPosition, shape)
    return newShapePlacement

def CalculateSplitBranchThickness(nrOfbranches):
    #Most of the time there exists a main branch, when a tree splits,
    thicknessPrecents =[]

    mainBranchMaxThickness=100 #precent
    mainBranchMinThickness= int(mainBranchMaxThickness/mainBranchMinimumThicknessReductionOnSplit)

    secondaryBranchMaxThickness = 98 #precent
    secondaryBranchMinThickness = int(secondaryBranchMaxThickness/secondaryBranchMinimumThicknessReductionOnSplit)

    mainBranchRayPrecent = random.randrange(mainBranchMinThickness,mainBranchMaxThickness)
    thicknessPrecents.append(mainBranchRayPrecent)

    for i in range(1,nrOfbranches):
        secondaryBranchThickness = random.randrange(secondaryBranchMinThickness,secondaryBranchMaxThickness)
        thicknessPrecents.append(secondaryBranchThickness)

    return thicknessPrecents



def Split(currentPosition, anglesIntervals, sphereRayInterval, initialAngles, currentRayPrecent):
    branchAngleSections = []
    branches = []
    branchSplitNumber = random.randint(splitInterval[0], splitInterval[1])

    anglesIntervals[1] = [0, math.pi*2]

    angleSection = anglesIntervals[1][1]/branchSplitNumber
    deadSection = anglesIntervals[1][1]/(branchSplitNumber+1)
    spinAngle = random.uniform(0, math.pi)
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


def GrowLeaves(TreeMeshName,LeafMeshName,hasEndingLeaf=1):
    scene = bpy.context.scene
    sourceObject = bpy.data.objects[LeafMeshName]
    parentObject = bpy.data.objects[TreeMeshName]

    global treeSegmentsManager

    for segment in treeSegmentsManager.terminalSegments:

        startPoint = segment.initialPoint
        angles = segment.angles
        endPoint = segment.endPoint
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

def Taper(raySize, taperRayPrecent):
    if taperRayPrecent>0:
        ray = raySize * taperRayPrecent/100
        ray = ray * taperRayPrecent/100
        return ray
    return 0


def GrowBranchingTrunk(currentPosition,initialShape,initialCircleNumber,stopRaySize,leafRaySize,minDeformedCircleRay,isMainBranch, anglesIntervals, currentRayPrecent,
                       rayReductionPrecentPerStep, raySphereInterval, startingSplitChance, splitChanceGain, deformities, previousPosition, oldAngles):
    bodyCilynder = []
    bodyCilynderFaces = []

    global currentCircleNumber
    global splitInterval
    global treeSegmentsManager

    mainBranch = 0

#==== Possible problems
    deformities = DeformitiesCheck(deformities, initialShape, minDeformedCircleRay)
#====
    taperedRay = Taper(minDeformedCircleRay, currentRayPrecent)

    # ===Stop Condition===
    if taperedRay < stopRaySize:
        treeSegmentThickness = tsGeo.SegmentThickness(currentRayPrecent, minDeformedCircleRay, currentRayPrecent,
                                                      taperedRay)
        treeSegment = tsGeo.TreeSegment(previousPosition, currentPosition, oldAngles, treeSegmentThickness,
                                        geo.CalculateDistanceBetweenTwoPoints(previousPosition, currentPosition))

        treeSegmentsManager.AddTerminalSegment(treeSegment)
        bodyCilynderFaces.append(geo.CalculateCircleFaceending(len(initialShape), initialCircleNumber))

        return [bodyCilynder, bodyCilynderFaces]
    # ===================


    newRayPrecent = currentRayPrecent - rayReductionPrecentPerStep
    previousPosition = currentPosition
    rayInterval = [(raySphereInterval[0] / 100) * currentRayPrecent, (raySphereInterval[1] / 100) * currentRayPrecent]
    positionAndAngles = geo.PickPointInSemiSphere(currentPosition, rayInterval=rayInterval,
                                                  initialAngles=[0, 0], anglesIntervals=anglesIntervals,
                                                  precision=precision)
    currentPosition = positionAndAngles[0]
    initialAngles = positionAndAngles[1]

    newShapePlacement = PlaceNewShape(currentPosition, deformities, initialAngles, initialShape, newRayPrecent, taperedRay)

    treeSegmentThickness = tsGeo.SegmentThickness(currentRayPrecent, minDeformedCircleRay, newRayPrecent, taperedRay)
    treeSegment = tsGeo.TreeSegment(previousPosition, currentPosition, initialAngles, treeSegmentThickness, geo.CalculateDistanceBetweenTwoPoints(previousPosition, currentPosition))

    if (taperedRay < leafRaySize) and (taperedRay > stopRaySize):
        treeSegmentsManager.AddThinSegment(treeSegment)

    currentRayPrecent = newRayPrecent
    bodyCilynder.append(newShapePlacement)
    currentCircleNumber += 1

    bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(initialShape), initialCircleNumber, currentCircleNumber))



#========================================================================================================================
    #==== Split Check ======
    chanceToSplit = random.randrange(0, 100)

    if chanceToSplit > startingSplitChance:
        #===== No Split ======
        startingSplitChance += splichanceGain
        branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber,
                                                   stopRaySize, leafRaySize, minDeformedCircleRay,
                                                   isMainBranch, anglesIntervals, currentRayPrecent,
                                                   rayReductionPrecentPerStep, raySphereInterval,
                                                   startingSplitChance, splitChanceGain, deformities,
                                                   previousPosition, initialAngles)
        bodyCilynder.extend(branchCirclesAndFaces[0])
        bodyCilynderFaces.extend(branchCirclesAndFaces[1])

    else:
        #==== Split =======
        treeSplit = Split(currentPosition, anglesIntervals, rayInterval, initialAngles=[0, 0], currentRayPrecent=currentRayPrecent)
        previousPosition = currentPosition
        previousCircleNumber = currentCircleNumber

        for branchIndex in range(0, len(treeSplit)):
            currentPosition = treeSplit[branchIndex][0]
            initialAngles = treeSplit[branchIndex][1]
            currentRayPrecent = treeSplit[branchIndex][2]
            sectionAngles = treeSplit[branchIndex][3]

            deformities = DeformitiesCheck(deformities, initialShape, minDeformedCircleRay)

            newShapePlacement = PlaceNewShape(currentPosition, deformities, initialAngles, initialShape, currentRayPrecent,
                                              taperedRay)

            bodyCilynder.append(newShapePlacement)
            currentCircleNumber += 1
            bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(initialShape), previousCircleNumber, currentCircleNumber))

            branchIdentifier = branchIndex + isMainBranch
            if branchIdentifier == mainBranch:
                branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber, stopRaySize, leafRaySize,
                                                           minDeformedCircleRay, branchIdentifier, anglesIntervals, currentRayPrecent,
                                                           rayReductionPrecentPerStep, raySphereInterval, startingSplitChance, splitChanceGain,
                                                           deformities, previousPosition, initialAngles)
                bodyCilynder.extend(branchCirclesAndFaces[0])
                bodyCilynderFaces.extend(branchCirclesAndFaces[1])
            else:
                deviantAnglesIntervals = DetermineZAngleInterval(initialAngles, anglesIntervals)
                deviantAnglesIntervals[1] = sectionAngles[1]
                branchCirclesAndFaces = GrowBranchingTrunk(currentPosition, initialShape, currentCircleNumber,
                                                           stopRaySize, leafRaySize, minDeformedCircleRay, branchIdentifier, deviantAnglesIntervals, currentRayPrecent,
                                                           rayReductionPrecentPerStep, raySphereInterval, startingSplitChance, splitChanceGain,
                                                           deformities, previousPosition, initialAngles)

                bodyCilynder.extend(branchCirclesAndFaces[0])
                bodyCilynderFaces.extend(branchCirclesAndFaces[1])

    #initial stump face removal
    return [bodyCilynder, bodyCilynderFaces]



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
    global treeSegmentManager
    global stopCircleRayPrecent, rayReductionPrecentPerStep, raySphereInterval
    global anglesIntervals, maxBranchAngleDeviation, minBranchAngleDeviation
    global splitInterval, startingSplitChance, splichanceGain
    treeSegmentManager = tsGeo.TreeSegmentManager()
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
    deformities = geo.SmoothRandom((0, 1), 1, nrCircleVertexes)
    # Stump============
    stumpCircles = sGeo.CalculateStumpCircles(nrCircleVertexes, circleRay, deformities, stumpAbruptness, height=1,
                                              finese=0.1)

    verts.extend(geo.ConvertCirclesToVerts(stumpCircles))
    faces.extend(sGeo.CalculateStumpFaces(stumpCircles))
    faces.append(geo.CalculateCircleFace(nrCircleVertexes))
    circle = stumpCircles[-1]

    deformities = geo.FindCircleDeformities(circle)

    global currentCircleNumber
    lastCircleNumber = len(stumpCircles) - 1
    currentCircleNumber = lastCircleNumber

    lastStumpCirclePosition = (0, 0, circle[0][2])

    global treeSegmentsManager
    treeSegmentsManager = tsGeo.TreeSegmentManager()

    if enableBark == False:
        deformities = []

    minDeformedCircleRay = geo.FindMinRayOfDeformedCircle(circle)
    stopRaySize = minDeformedCircleRay * stopCircleRayPrecent / 100
    leafRaySize = minDeformedCircleRay * leafRayStart / 100

    trunk = GrowBranchingTrunk(currentPosition=lastStumpCirclePosition, initialShape=circle,
                               initialCircleNumber=lastCircleNumber, stopRaySize=stopRaySize,
                               leafRaySize=leafRaySize, minDeformedCircleRay=minDeformedCircleRay,
                               isMainBranch=0, anglesIntervals=anglesIntervals, currentRayPrecent=100,
                               rayReductionPrecentPerStep=rayReductionPrecentPerStep,
                               raySphereInterval=raySphereInterval, startingSplitChance=startingSplitChance,
                               splitChanceGain=splichanceGain, deformities=deformities,
                               previousPosition=lastStumpCirclePosition, oldAngles=[0, 0])

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

    GrowLeaves("Tree", leafObjectName)
    JoinTreeObjectsWithTree(myobject)


#====Globals=====
currentCircleNumber = 0
#===Parameters===
nrCircleVertexes=6
precision = 2
circleRay=3
stumpAbruptness = 3

#Bark
enableBark = False
barkMutationChance = 0.5
barkMutationFactor = 4  #Lower factor = more noticeable, Greater = less noticeable

#Branching
stopCircleRayPrecent = 1
rayReductionPrecentPerStep = 3
raySphereInterval = [circleRay,circleRay*2]

anglesIntervals = [[-math.pi/5,math.pi/5],[0,math.pi*2]]
maxBranchAngleDeviation = math.pi/1.2
minBranchAngleDeviation = -maxBranchAngleDeviation #anglesIntervals[0][0]

splitInterval = [2,3]
startingSplitChance = 20
splichanceGain = 0.5

mainBranchMinimumThicknessReductionOnSplit =1.1
secondaryBranchMinimumThicknessReductionOnSplit = 1.1
#Leaves
leafRayStart = 5
leavesPerBranch = [5,10]
leavesDistance = 1# greater number = smaller distance between leaves
leafRotationAngleDeviation = [-30,30]
#Materials
barkMaterialName = "Clay"
#Objects
leafObjectName = "Leaf"
#================
if __name__ == "__main__":
    CreateTree()



