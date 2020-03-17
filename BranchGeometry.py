import bpy
import math
import random
import os
from copy import deepcopy
utilityScriptPath="C:\\Users\\Bogdan\\PycharmProjects\\BlendScriptAttempt\\GeneralGeometry.py" #os.path.join(os.path.dirname(os.path.abspath( __file__ )),"GeneralGeometry.py").replace("\\Scripting.blend",'')

import importlib.util
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)

inputRules = ['1', '0']
outputRules = ["11", "1[0]10]0"]
ruleMeaning = dict()
startStep = "0"

def setInputRules(rules):
    global inputRules
    inputRules = rules

def setOutputRules(rules):
    global outputRules
    outputRules = rules

def setStartStep(startElement):
    global startStep
    if(startElement in outputRules):
        startStep = startElement
    else:
        raise Exception("Element not in rules!")

'''
    the meaningDictionary parameter
    must contain the keys save,load,draw,rotateOnX,rotateOnY,rotateOnZ,scale
'''
def setRuleMeaning(meaningDictionary):
    global ruleMeaning
    ruleMeaning=meaningDictionary


def generateFractalString(iteration):
        result = startStep
        temp = ""
        for i in range(iteration):
            for j in range(len(result)):
                for k in range(len(inputRules)):
                    if (result[j] == inputRules[k]):
                        temp += outputRules[k]
                        break
                    if (k == len(inputRules) - 1):
                        temp += result[j]
            result = temp
            temp = ""
        return result

def drawFractalTest(input,angleRad,shape):
    stack=[]
    shapeStack =[]
    directionStack = []
    circleStack = []

    stepVector = (0,0,5)
    currentPosition = (0,0,0)

    bodyCilynder=[]

    bodyCilynderFaces = []

    bodyCilynder.append(shape)

    nrCircle = 0
    initialCircle = 0

    for x in input:
        if (x == '1'):
            currentPosition = geo.sum_touples(currentPosition,stepVector)
            bodyCilynder.append(geo.addVectorToVerts(currentPosition,shape))

            nrCircle += 1
            bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), initialCircle, nrCircle))
            initialCircle = nrCircle
        elif (x == '0'):
            currentPosition = geo.sum_touples(currentPosition,stepVector)
            bodyCilynder.append(geo.addVectorToVerts(currentPosition,shape))

            nrCircle += 1
            bodyCilynderFaces.extend(geo.CreateFaceBetweenTwoCircles(len(shape), initialCircle, nrCircle))
            initialCircle = nrCircle
        elif (x == '['):
            stack.append(list(currentPosition))
            shapeStack.append(shape)
            directionStack.append(stepVector)
            circleStack.append(nrCircle)

            shape = geo.rotateVerticesOnX(len(shape),shape,-angleRad)
            stepVector = geo.sum_touples(stepVector,(0,math.sin(angleRad)*5,0))

            stack.append(list(currentPosition))
            shapeStack.append(shape)
            directionStack.append(stepVector)
            circleStack.append(nrCircle)

        elif (x == ']'):
                position = tuple(stack.pop())
                currentPosition = position
                shape = shapeStack.pop()
                stepVector = directionStack.pop()
                initialCircle = circleStack.pop()


                shape = geo.rotateVerticesOnX(len(shape), shape, angleRad)
                stepVector = geo.sum_touples(stepVector, (0, math.sin(-angleRad)*5, 0))

    return [bodyCilynder,bodyCilynderFaces]

'''
def drawFractal(fractalString):
    directionVector = (0,0,1)
    stack = []
    directionStack = []
    for step in fractalString:
        for key in ruleMeaning.keys():
            if(key == "draw"):
                if(step==ruleMeaning[key]):
'''



