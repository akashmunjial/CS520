import heapq
import math
import osmnx
from backend.keys import api_key 
from backend.currObj import CurrObj

class AStar:
    def __init__(self, graph, max_min, limit):
        self.graph = graph
        self.max_min = max_min
        self.limit = limit
        
    def heuristic(self, node1, node2):
        n1 = self.graph.get_coords(node1)
        n2 = self.graph.get_coords(node2)
        # TODO: maybe somehow incorporate z1 and z2 from elevation data???
        # return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)
        return max(0,(n2['z']-n1['z'])**3) if self.max_min == 'minimal' else -max(0,(n2['z']-n1['z'])**3)

    def distance(self, node1, node2):
        return self.graph.get_edge_distance(node1, node2) # TODO: what if len(array) != 1


    def search(self, start, end):
        visitedList = set()
        objPointers = {start: CurrObj(start, None, 0, 0, 0)}
        currList = [objPointers[start]]

        while len(currList) > 0:
            curr = heapq.heappop(currList)
            visitedList.add(curr.getNode())
            if curr.getNode() == end:
                path = []
                while curr.getParent() is not None:
                    path.insert(0,curr.getNode())
                    curr = objPointers[curr.getParent()]
                path.insert(0,curr.getNode())
                print('Path Found: ', path)
                return path
            neighbors = self.graph.get_neighbors(curr.getNode())
            for n in neighbors:
                if n in visitedList:
                    continue
                elif n not in objPointers:
                    dist = curr.getActualDist()+self.distance(curr.getNode(),n)
                    if dist <= self.limit:
                        obj = CurrObj(n, curr.getNode(), self.heuristic(curr.getNode(), n), dist, curr.getElevationData()+self.heuristic(curr.getNode(), n))
                        heapq.heappush(currList, obj)
                        objPointers[n] = obj
                else:
                    dist = curr.getActualDist()+self.distance(curr.getNode(),n)
                    if dist <= self.limit:
                        obj = objPointers[n]
                        if obj.getHeuristicDist() > self.heuristic(curr.getNode(), n):
                            obj.setParent(curr.getNode())
                            obj.setActualDist(dist)
                            obj.setHeuristicDist(self.heuristic(curr.getNode(), n))
                            obj.setElevationData(curr.getElevationData()+self.heuristic(curr.getNode(), n))
                            heapq.heapify(currList)
        print("No path found")
        return []

