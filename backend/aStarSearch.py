import heapq
import math
import osmnx
from backend.keys import api_key 
from backend.currObj import CurrObj

class AStar:
    def __init__(self, graph):
        self.graph = graph
        
    def heuristic(self, node1, node2):
        n1 = self.graph.get_coords(node1)
        n2 = self.graph.get_coords(node2)
        # TODO: maybe somehow incorporate z1 and z2 from elevation data???
        return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)

    def distance(self, node1, node2):
        return self.graph.get_edge_distance(node1, node2) # TODO: what if len(array) != 1


    def search(self, start, end):
        visitedList = set()
        objPointers = {start: CurrObj(start, None, 0+self.heuristic(start,end), 0)}
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
                    obj = CurrObj(n, curr.getNode(), dist+self.heuristic(n,end), dist)
                    heapq.heappush(currList, obj)
                    objPointers[n] = obj
                else:
                    dist = curr.getActualDist()+self.distance(curr.getNode(),n)
                    obj = objPointers[n]
                    if obj.getHeuristicDist() > dist+self.heuristic(n,end):
                        obj.setParent(curr.getNode())
                        obj.setActualDist(dist)
                        obj.setHeuristicDist(dist+self.heuristic(n,end))
                        heapq.heapify(currList)
        print("No path found")
        return []

