import bpy
import math
import random
import decimal
import os
utilityScriptPath="C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\GeneralGeometry.py" #os.path.join(os.path.dirname(os.path.realpath( __file__ )),"GeneralGeometry.py").replace("\\Scripting.blend",'')

import importlib.util
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)



# mesh arrays
#conteaza ordinea
#(x,z,y) desi in blender axele sunt puse ca si (x,y,z)
verts = []
faces = []
edges = []

#=============== Tree Stump Geometry ================================
lastLowerStumpCirclePrecent = 100

#Uses logarthim to generate curve
#Sets lastLowerStumpCirclePrecent
def CalculateLowerStump(nrCircleVertexes,ray,deformities,finese=0.1):
    logCurveStart = 3
    logCurveStop = 2

    stumpLowerCircles=[]
    precents =[]
    for x in geo.drange(logCurveStart, logCurveStop, finese):
        reducedCirclePrecent = 100 * (-math.log(x)) / -math.log(logCurveStart)
        precents.append(reducedCirclePrecent)

    global lastLowerStumpCirclePrecent
    nrCircles = 0
    for circlePrecent in precents:
        resizedCircle= geo.LowerStumpCalculaeResizedDeformedCircle(nrCircleVertexes, ray, circlePrecent, deformities)
        lastLowerStumpCirclePrecent = circlePrecent
        for resizedVertexNr in range(0,nrCircleVertexes):
            resizedCircle[resizedVertexNr]= geo.replace_at_index1(resizedCircle[resizedVertexNr],2,resizedCircle[resizedVertexNr][2]+nrCircles*finese)
        nrCircles+=1

        stumpLowerCircles.append(resizedCircle)
    return stumpLowerCircles

#Warning: uses lastLowerStumpCirclePrecent global Variable
def CalculateUpperStump(nrCircleVertexes,ray,deformities,lastLowerStumpCircle,abruptness=2,height=1,finese=0.1):
    logCurveLowerStump = 3
    logCurveStart = 2
    logCurveStop = 1.4

    precents =[]
    for x in geo.drange(logCurveStart, logCurveStop, finese/2):
        reducedCirclePrecent = 100 * (-math.log(x)) / -math.log(logCurveLowerStump)
        precents.append(reducedCirclePrecent)


    maxRay=max(deformities)
    minRay=min(deformities)
    nrOfSmoothSteps=int(height/finese)
    heightStep=height/nrOfSmoothSteps
    rayReduction=(maxRay-minRay)/(nrOfSmoothSteps)

    #TODO Find a better way to introduce noise
    noise = random.randrange(2,4,1)

    smoothDeformities=deformities.copy()

    smoothCircles =[]

    for step in range(0,nrOfSmoothSteps-noise):
        for i in range(0,nrCircleVertexes):
            if(smoothDeformities[i]>(maxRay-step*rayReduction)):
                smoothDeformities[i]=maxRay-step*rayReduction
        smoothCircle = geo.LowerStumpCalculaeResizedDeformedCircle(nrCircleVertexes,ray,precents[step],smoothDeformities)
        for i in range(0,nrCircleVertexes):
            smoothCircle[i] = geo.replace_at_index1(smoothCircle[i],2,lastLowerStumpCircle[i][2]+(heightStep*(step+1))*abruptness)
        smoothCircles.append(smoothCircle)

    return smoothCircles




def CalculateStumpCircles(nrCircleVertexes,ray,deformities,abruptness,height,finese=0.1):
    stumpCircles = []

    lowerStumpCircles = CalculateLowerStump(nrCircleVertexes,ray,deformities,finese)
    upperStumpCircles = CalculateUpperStump(nrCircleVertexes,ray,deformities,lowerStumpCircles[-1],abruptness,height,finese)
    for circle in lowerStumpCircles:
        stumpCircles.append(circle)
    for circle in upperStumpCircles:
        stumpCircles.append(circle)

    return stumpCircles

def CalculateStumpFaces(stumpCircles):
    stumpFaces =[]
    stumpVerts = geo.ConvertCirclesToVerts(stumpCircles)
    stumpFaces.extend(geo.CreateShapeOutOfCircleVertexes(len(stumpCircles[0]),stumpVerts))
    return stumpFaces

#===============================================================
#===Parameters===
nrCircleVertexes=60
circleRay=2
stumpAbruptness = 2
#================
if __name__ == "__main__":
    deformities = geo.SmoothRandom((0, 2), 1, nrCircleVertexes)
    stumpCircles = CalculateStumpCircles(nrCircleVertexes, circleRay, deformities, stumpAbruptness, height=1, finese=0.1)
    verts.extend(geo.ConvertCirclesToVerts(stumpCircles))
    faces.extend(CalculateStumpFaces(stumpCircles))
    faces.append(geo.CalculateCircleFace(nrCircleVertexes,verts))
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





