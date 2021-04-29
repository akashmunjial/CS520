import math
import heapq

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
        return abs(n2['z']-n1['z']) if self.max_min == 'minimal' else -abs(n2['z']-n1['z'])

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
                    if dist <= self.limit:
                        obj = CurrObj(n, curr.getNode(), dist+self.heuristic(n,end), dist)
                        heapq.heappush(currList, obj)
                        objPointers[n] = obj
                else:
                    dist = curr.getActualDist()+self.distance(curr.getNode(),n)
                    if dist <= self.limit:
                        obj = objPointers[n]
                        if obj.getHeuristicDist() > dist+self.heuristic(n,end):
                            obj.setParent(curr.getNode())
                            obj.setActualDist(dist)
                            obj.setHeuristicDist(dist+self.heuristic(n,end))
                            heapq.heapify(currList)
        print("No path found")
        return []

class Graph:
    def __init__(self):
        super().__init__()
        self.nodes = {}

    def get_edge_distance(self, n1, n2):
        return math.sqrt((self.nodes[n1].x-self.nodes[n2].x)**2 + (self.nodes[n1].y-self.nodes[n2].y)**2)

    def get_coords(self, n):
        return {'z': self.nodes[n].z}

    def get_neighbors(self, n):
        return self.nodes[n].neighbors


class Node:
    def __init__(self,x,y,z):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.neighbors = []

start = Node(0,0,0)
end = Node(10,10,0)
m1 = Node(5,5,10)
m2 = Node(10,5,0)
start.neighbors.append('2')
start.neighbors.append('3')
m1.neighbors.append('4')
m2.neighbors.append('4')

graph = Graph()
graph.nodes = {'1':start, '2':m1,'3':m2,'4':end}


s = AStar(graph, 'maximal', 1.5*14)
s.search('1','4')