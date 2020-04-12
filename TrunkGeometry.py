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

def CalculateSplitBranchThickness(nrOfbranches):
    #Most of the time there exists a main branch, when a tree splits,
    thicknessPrecents =[]

    mainBranchMaxThickness=80 #precent
    mainBranchMinThickness=mainBranchMaxThickness/2

    secondaryBranchMaxThickness = 60 #precent
    secondaryBranchMinThickness = secondaryBranchMaxThickness/2

    mainBranchRayPrecent = random.randrange(mainBranchMinThickness,mainBranchMaxThickness)
    thicknessPrecents.append(mainBranchRayPrecent)

    for i in range(1,nrOfbranches):
        secondaryBranchThickness = random.randrange(secondaryBranchMinThickness,secondaryBranchMaxThickness)
        thicknessPrecents.append(secondaryBranchThickness)

    return thicknessPrecents





def Split(currentPosition,circle,circleNumber,anglesIntervals,sphereRayInterval,initialAngles,branchSplitNumber):
    circleRay = geo.FindMinRayOfDeformedCircle(circle)

    branches = []
    angleSection = anglesIntervals[1]/branchSplitNumber

    for i in range(1,branchSplitNumber):
        sectionAngleIntervals =[anglesIntervals[0],[angleSection*i,angleSection*(i+1)]]
        branchPositionAndAngles = geo.PickPointInSemiSphere(currentPosition,sphereRayInterval,initialAngles, sectionAngleIntervals, precision)
        branches.append(branchPositionAndAngles)
    branchPrecents = CalculateSplitBranchThickness(branchSplitNumber)
    for i in range(1,branchSplitNumber):
        branches[i].append(branchPrecents[i])

    return branches


def GrowTrunk(iterations,currentPosition,shape,initialCircle,randomIntervalTouple,deformities,mutationChance,mutationFactor,randomIntervalDecimalNumber=1):
    bodyCilynder=[]
    bodyCilynderFaces = []
    bodyCilynder.append(shape)

    nrCircle = initialCircle

    initialAngles = [0,0]
    anglesIntervals = [[0,math.pi/6],[0,math.pi*2]]
    splitInterval = [2,3]

    for i in range(1,iterations):
        positionAndAngles = geo.PickPointInSemiSphere(currentPosition, rayInterval = [1,1], initialAngles = [0,0], anglesIntervals = anglesIntervals, precision = precision)

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

    #remove the initial stump face
    bodyCilynder.pop(0)
    return [bodyCilynder,bodyCilynderFaces]


#==============================================================
#===Parameters===
nrCircleVertexes=60
precision = 2
circleRay=2
stumpAbruptness = 2
barkMutationChance=0.5
barkMutationFactor=4 #Lower factor = more noticeable, Greater = less noticeable
#================
#fractalString = bGeo.generateFractalString(6)
#fractal = bGeo.drawFractalTest(fractalString,math.pi/6,circle1)

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

trunk = GrowTrunk(100,(0,0,circle[0][2]),circle,lastCircleNumber,(-0.2,0.2),deformities,barkMutationChance,barkMutationFactor,1)
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

