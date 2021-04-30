class CurrObj(object):
    def __init__(self, node, parent, heuristicDist, actualDist, elevationGain):
        super().__init__()
        self.node = node
        self.parent = parent
        self.heuristicDist = heuristicDist
        self.actualDist = actualDist
        self.elevationGain = elevationGain

    def getParent(self):
        return self.parent

    def getNode(self):
        return self.node

    def getActualDist(self):
        return self.actualDist

    def getHeuristicDist(self):
        return self.heuristicDist

    def setParent(self, parent):
        self.parent = parent
    
    def setActualDist(self, dist):
        self.actualDist = dist
    
    def setHeuristicDist(self,dist):
        self.heuristicDist = dist

    def getElevationData(self):
        return self.elevationGain

    def setElevationData(self, elevationGain):
        self.elevationGain  = elevationGain

    def __lt__(self, other):
        return self.heuristicDist < other.heuristicDist

    