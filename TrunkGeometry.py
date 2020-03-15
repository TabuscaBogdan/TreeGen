import bpy
import bmesh
import math
import random
import mathutils
import os
utilityScriptPath= os.path.join(os.path.dirname(os.path.abspath( __file__ )),"GeneralGeometry.py")

import importlib.util
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)

branchScriptPath= os.path.join(os.path.dirname(os.path.abspath( __file__ )),"BranchGeometry.py")
branchSpec = importlib.util.spec_from_file_location("BranchGeometry", branchScriptPath)
branchGeometry = importlib.util.module_from_spec(branchSpec)
branchSpec.loader.exec_module(branchGeometry)

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
nrCircleVertexes =60
ray=2

bm = bmesh.new()
matrix_world=(((1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0)))

deformities = geo.SmoothRandom((0, 2), 1, nrCircleVertexes)

circle1 = geo.CalculateVertexDeformedCircle(nrCircleVertexes,ray,deformities)
print(circle1)
circle2 = geo.CalculateVertexDeformedCircle(nrCircleVertexes,ray,deformities)

vec = (0, 1, 1)

circle2 = translateVertices(nrCircleVertexes,circle2,vec,2)
circle2 = rotateVerticesOnZ(nrCircleVertexes,circle2,math.pi/4)
circle1 = translateVertices(nrCircleVertexes,circle1,(-1,-1,-2),3)

print(circle1)
print(circle2)
verts.extend(circle1)
verts.extend(circle2)

#=======================
faces.extend(geo.CreateShapeOutOfCircleVertexes(nrCircleVertexes,verts))
geo.CalculateCircleFace(nrCircleVertexes)
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
