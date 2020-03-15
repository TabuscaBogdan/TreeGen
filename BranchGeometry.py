import bpy
import math
import random
import os
utilityScriptPath= os.path.join(os.path.dirname(os.path.abspath( __file__ )),"GeneralGeometry.py")

import importlib.util
utilitySpec = importlib.util.spec_from_file_location("GeneralGeometry", utilityScriptPath)
geo = importlib.util.module_from_spec(utilitySpec)
utilitySpec.loader.exec_module(geo)

inputRules = []
outputRules = []
startStep = None

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


def generateFractalString():
    def generate(iteration):
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