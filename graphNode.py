class GraphNode:
    def __init__(self, value, neighbors: set):
        self.value = value
        self.neighbors = neighbors

    def getValue(self):
        return self.value

    def getNeighbors(self):
        return self.neighbors

    def addNeighbor(self, neighbor):
        self.neighbors.add(neighbor)