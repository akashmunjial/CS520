class CurrObj(object):
    def __init__(self, node, parent, heuristicDist, actualDist):
        super().__init__()
        self.node = node
        self.parent = parent
        self.heuristicDist = heuristicDist
        self.actualDist = actualDist

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

    def __lt__(self, other):
        return self.heuristicDist < other.heuristicDist