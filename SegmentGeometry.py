class SegmentThickness:
    def __init__(self, startRayPrecent, startRaySize, endRayPrecent, endRaySize):
        self.startRayPrecent = startRayPrecent
        self.startRaySize = startRaySize
        self.endRayPrecent = endRayPrecent
        self.endRaySize = endRaySize


class TreeSegment:
    def __init__(self, initialPoint, endPoint, angles, thickness, length):
        self.initialPoint = initialPoint
        self.endPoint = endPoint
        self.angles = angles
        self.thickness = thickness
        self.length = length

class TreeSegmentManager:
    def __init__(self):
        self.thinSegmentNumber = 0
        self.thinSegments = []
        self.terminalSegmentsNumber = 0
        self.terminalSegments = []

    def AddThinSegment(self, treeSegment):
        self.thinSegmentNumber += 1
        self.thinSegments.append(treeSegment)

    def AddTerminalSegment(self, treeSegment):
        self.terminalSegmentsNumber += 1
        self.terminalSegments.append(treeSegment)