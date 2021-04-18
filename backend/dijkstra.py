import heapq
import math
import osmnx
from collections import defaultdict
from backend.keys import api_key

'''
Essentially follows the implementation here: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue
'''
class Dijkstra:
    def __init__(self, graph):
        self.graph = graph

    def distance(self, node1, node2):
        return self.graph.get_edge_data(node1, node2)[0]['length'] # TODO: what if len(array) != 1

    def search(self, start, end):
        prev = {}
        dist = defaultdict(lambda: math.inf)
        visited = set()
        priority_queue = []

        prev[start] = None
        dist[start] = 0
        heapq.heappush(priority_queue, (dist[start], start))

        while len(priority_queue) > 0:
            curr_dist, curr_node = heapq.heappop(priority_queue)

            '''Mark as visited, which implies dist[curr_node] currently
            contains shortest distance between 'start' and 'curr_node'
            '''
            visited.add(curr_node)
            if curr_node == end:
                path = [end]
                predecessor = prev[end]
                while predecessor is not None:
                    path.append(predecessor)
                    predecessor = prev[predecessor]
                path.reverse() # Make list begin with 'start' node
                print('Path Found: ', path)
                return path

            neighbors = self.graph.neighbors(curr_node)
            for n in neighbors:
                if n in visited:
                    continue
                alt_path_dist = curr_dist + self.distance(curr_node, n)
                if alt_path_dist < dist[n]:
                    dist[n] = alt_path_dist
                    prev[n] = curr_node
                    heapq.heappush(priority_queue, (alt_path_dist, n))

        """
        Should we only allow a node to appear once in the priority queue? This
        is memory-efficient, but requires us to do a linear search every time we
        want to update a node's priority queue value.
        """

        print("No path found")
        return []

