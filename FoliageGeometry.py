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

def refineEulerAngles(angles):
    #sign = (angles[0] > 0) - (angles[0] < 0)
    #xRot = sign * (abs(angles[0]) % math.pi)
    xRot = 0

    #sign = (angles[1] > 0) - (angles[1] < 0)
    #yRot = sign * (abs(angles[1]) % math.pi)
    yRot = 0

    zRot = angles[2]

    return [xRot, yRot, zRot]

def AddLeaf(angles, endPoint, scene, sourceObject):
    global treeObjects

    newObject = sourceObject.copy()
    newObject.data = sourceObject.data.copy()
    newObject.location = endPoint

    newObject.rotation_euler = (angles[0], angles[1], angles[2])
    # newObject.parent = parentObject
    scene.collection.objects.link(newObject)
    treeObjects.append(newObject)

def WindDeviation():
    minorDeviation = random.randint(int(leafRotationAngleDeviation[0] / 2), int(leafRotationAngleDeviation[1] / 2))
    yLeafRotation = (math.pi / 180) * minorDeviation
    minorDeviation = random.randint(int(leafRotationAngleDeviation[0] / 2), int(leafRotationAngleDeviation[1] / 2))
    xLeafRotation = (math.pi / 180) * minorDeviation
    return xLeafRotation, yLeafRotation

def GrowLeaves(TreeMeshName,LeafMeshName, useThinSegments=False):
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
        hasEndingLeaf = 1
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
            eulerAngles = geo.getEulerAnglesFromSphereAngles(angles)
            AddLeaf(eulerAngles, endPoint, scene, sourceObject)

        leafNumber = random.randint(leavesPerBranch[0], leavesPerBranch[1])
        maxLeavesPairs = leavesPerBranch[1]/2
        if maxLeavesPairs == 0:
            maxLeavesPairs += 1

        unitDistance = (distance/maxLeavesPairs)/leavesDistance
        for i in range(0, leafNumber):
            leafDistance = (distance - (unitDistance * (i/2))) / distance
            x = startPoint[0] + leafDistance * (endPoint[0] - startPoint[0])
            y = startPoint[1] + leafDistance * (endPoint[1] - startPoint[1])
            z = startPoint[2] + leafDistance * (endPoint[2] - startPoint[2])
            position = tuple([x, y, z])

            if i % 2 == 1:
                deviation = random.randint(leafRotationAngleDeviation[0],leafRotationAngleDeviation[1])
                zLeafRotation = (math.pi/180)*deviation + extraRotation[2]
                xLeafRotation, yLeafRotation = WindDeviation()

                eulerAngles = geo.getEulerAnglesFromSphereAngles(angles)
                eulerAngles = refineEulerAngles(eulerAngles)
                eulerAngles = [eulerAngles[0] + xLeafRotation, eulerAngles[1] + yLeafRotation, eulerAngles[2] + zLeafRotation]

                AddLeaf(eulerAngles, position, scene, sourceObject)
            else:
                deviation = random.randint(leafRotationAngleDeviation[0], leafRotationAngleDeviation[1])
                zLeafRotation = math.pi + (math.pi / 180) * deviation + extraRotation[2]
                xLeafRotation, yLeafRotation = WindDeviation()

                eulerAngles = geo.getEulerAnglesFromSphereAngles(angles)
                eulerAngles = refineEulerAngles(eulerAngles)
                eulerAngles = [eulerAngles[0] + xLeafRotation, eulerAngles[1] + yLeafRotation,
                               eulerAngles[2] + zLeafRotation]

                AddLeaf(eulerAngles, position, scene, sourceObject)


def GrowFoliage(treeObject):
    if (leafMeshName == "") or (leafMeshName is None):
        return

    start_time = time.time()
    GrowLeaves(treeMeshName, leafMeshName, useThinSegments=False)
    GrowLeaves(treeMeshName, leafMeshName, useThinSegments=True)
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