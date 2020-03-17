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

verts = []
faces = []
edges = []

def matmult(X,Y):
        result = []
        for i in range(len(X)):
            result.append([])
            for j in range(len(Y[0])):
                result[i].append(0)
                for k in range(len(Y)):
                    result[i][j] += X[i][k] * Y[k][j]
        return result


#================== Geometry ==================================
def translateVertices(nrCircleVertexes,circleVertexes,vector,unit=1):
    movedVertices=[]
    for i in range(0, nrCircleVertexes):
        x=circleVertexes[i][0] + vector[0]*unit
        y=circleVertexes[i][1] + vector[1]*unit
        z=circleVertexes[i][2] + vector[2]*unit
        movedVertices.append((x, y, z))
    return movedVertices

#rotation
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


#scaleing

#==============================================================
nrCircleVertexes = 60
ray=2

bm = bmesh.new()
matrix_world=(((1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0)))

deformities = [] #geo.SmoothRandom((0, 2), 1, nrCircleVertexes)

circle1 = geo.CalculateVertexDeformedCircle(nrCircleVertexes,ray,deformities)
fractalString = bGeo.generateFractalString(6)
fractal = bGeo.drawFractalTest(fractalString,math.pi/6,circle1)
for tCircle in fractal[0]:
    verts.extend(tCircle)

#=======================
faces.extend(fractal[1])
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

print(bm.verts)
