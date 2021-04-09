from graphNode import GraphNode
import heapq

class AStar:
    def __init__(self, graph):
        self.graph = graph
        
    def heuristic(self, node1, node2):
        return 0 #Dummy value

    def search(self, start, end):
        visitedList = set()
        currentListWithCosts = [] # Stores the actual cost
        currentListNodes = set() # Store only the nodes, used for checking if the node already is in currentList and its cost need to be updated
        currentListNodes.add(start)
        heapq.heappush(currentListWithCosts, [0,0, start]) # maintain a heap the values are [current length+heuristic, current length, node]
        parentRelation = {}
        parentRelation[start] = None

        while len(currentListNodes) > 0:
            curr = heapq.heappop(currentListWithCosts)
            visitedList.add(curr[2])
            currentListNodes.discard(curr[2])
            if curr[2] == end:
                path = []
                while end is not None:
                    path.insert(0,end)
                    end = parentRelation[end]
                print('Path Found: ', path)
            neighbors = curr[2].getNeighbors()
            for n in neighbors:
                if n in visitedList:
                    continue
                elif n not in currentListNodes:
                    currentListNodes.add(n)
                    heapq.heappush(currentListWithCosts, [curr[1]+self.heuristic(n,end), curr[1]+1, n])
                    parentRelation[n] = curr[2]
                else:
                    i = self.heapFind(currentListWithCosts, n)
                    if i == -1:
                        continue
                    elif currentListWithCosts[i][0] > curr[1]+1+self.heuristic(n, end):
                        parentRelation[n] = curr[2]
                        currentListWithCosts[i][0] = curr[1]+1+self.heuristic(n, end)
                        heapq.heapify(currentListWithCosts) #re-establish the heap
        print("No path found")
                    
    #Find the index of a node in the heap
    def heapFind(self, heap, node):
        for i in range(len(heap)):
            if heap[i][2] == node:
                return i
        return -1

