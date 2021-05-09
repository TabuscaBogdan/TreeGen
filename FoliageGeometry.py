import bpy
import random
import math
import time

import importlib.util
utilityScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\GeneralGeometry.py"
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)

segmentScriptPath= "C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\SegmentGeometry.py"
segmentSpec = importlib.util.spec_from_file_location("SegmentGeometry", segmentScriptPath)
tsGeo = importlib.util.module_from_spec(segmentSpec)
segmentSpec.loader.exec_module(tsGeo)

treeObjects = []
treeSegmentsManager = tsGeo.TreeSegmentManager()
leavesPerBranch = []
leavesDistance = 1
leafRotationAngleDeviation = []
treeMeshName = ""
leafMeshName = ""

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

def WindDeviation():
    minorDeviation = random.randint(int(leafRotationAngleDeviation[0] / 2), int(leafRotationAngleDeviation[1] / 2))
    yLeafRotation = (math.pi / 180) * minorDeviation
    minorDeviation = random.randint(int(leafRotationAngleDeviation[0] / 2), int(leafRotationAngleDeviation[1] / 2))
    xLeafRotation = (math.pi / 180) * minorDeviation
    return xLeafRotation, yLeafRotation

def GrowLeaves(TreeMeshName,LeafMeshName,hasEndingLeaf=1,useThinSegments=False):
    scene = bpy.context.scene
    sourceObject = bpy.data.objects[LeafMeshName]
    parentObject = bpy.data.objects[TreeMeshName]

    global treeSegmentsManager
    treeSegments = []
    if useThinSegments:
        treeSegments = treeSegmentsManager.thinSegments
        hasEndingLeaf = 0
    else:
        treeSegments = treeSegmentsManager.terminalSegments
    for segment in treeSegments:

        startPoint = segment.initialPoint
        angles = segment.angles
        endPoint = segment.endPoint
        distance = segment.length

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
            if i % 2 == 1:
                leafDistance = (distance-(unitDistance * i))/distance
                x = startPoint[0]+leafDistance*(endPoint[0]-startPoint[0])
                y = startPoint[1] + leafDistance * (endPoint[1] - startPoint[1])
                z = startPoint[2] + leafDistance * (endPoint[2] - startPoint[2])
                position = tuple([x,y,z])

                deviation = random.randint(leafRotationAngleDeviation[0],leafRotationAngleDeviation[1])
                zLeafRotation =(math.pi/180)*90+(math.pi/180)*deviation + extraRotation[2]
                xLeafRotation, yLeafRotation = WindDeviation()
                secondaryRotations = [xLeafRotation, yLeafRotation, zLeafRotation]

                AddLeaf(angles, secondaryRotations, position, scene, sourceObject)
            else:
                deviation = random.randint(leafRotationAngleDeviation[0], leafRotationAngleDeviation[1])
                zLeafRotation = math.pi + (math.pi / 180) * deviation + extraRotation[2]
                xLeafRotation, yLeafRotation = WindDeviation()
                secondaryRotations = [xLeafRotation, yLeafRotation, zLeafRotation]
                AddLeaf(angles, secondaryRotations, position, scene, sourceObject)


def GrowFoliage(treeObject):
    if (leafMeshName == "") or (leafMeshName is not None):
        return

    start_time = time.time()
    GrowLeaves(treeMeshName, leafMeshName, hasEndingLeaf=1, useThinSegments=False)
    GrowLeaves(treeMeshName, leafMeshName, hasEndingLeaf=0, useThinSegments=True)
    print("Grow Leaves Execution time: %s" % (time.time() - start_time))
    start_time = time.time()
    JoinTreeObjectsWithTree(treeObject)
    print("Join Leaves Execution time: %s" % (time.time() - start_time))


def SetFoliageParameters(treeSegManager, treeObjName, leafObjName, intervalOfleavesPerBranch, leafDistance, leafAngleDeviation):
    global treeSegmentsManager
    global treeMeshName
    global leafMeshName
    global leavesPerBranch
    global leavesDistance
    global leafRotationAngleDeviation
    treeSegmentsManager = treeSegManager
    treeMeshName = treeObjName
    leafMeshName = leafObjName
    leavesPerBranch = intervalOfleavesPerBranch
    leavesDistance = leafDistance
    leafRotationAngleDeviation = leafAngleDeviation