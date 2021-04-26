import heapq
import math
import osmnx
from collections import defaultdict
from backend.keys import api_key

'''
Essentially follows the implementation here: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue
'''
class Dijkstra:
    def __init__(self, graph, use_elevation=False, max_path_len=None):
        self.graph = graph
        if use_elevation and max_path_len is None:
            assert max_path_len is not None, "If we are going to use elevation data, we need a maximum path length we cannot exceed"
        self.use_elevation = use_elevation

    def distance(self, node1, node2):
        return self.graph.get_edge_distance(node1, node2)

    def elevation(self, node):
        return self.graph.nodes[node]['elevation']

    def search(self, start, end):
        prev = {}
        dist = defaultdict(lambda: math.inf)
        visited = set()
        priority_queue = []
        subtract = {}

        prev[start] = None
        dist[start] = 0
        heapq.heappush(priority_queue, (dist[start], start, 0.))
        subtract[start] = 0.
        while len(priority_queue) > 0:
            curr_dist, curr_node = heapq.heappop(priority_queue)

            '''Mark as visited, which implies dist[curr_node] currently
            contains shortest distance between 'start' and 'curr_node'
            '''
            visited.add(curr_node)
            if curr_node == end:
                path = [end]
                predecessor = prev[end]
                subtract_total = subtract[end] # Initialize
                while predecessor is not None:
                    path.append(predecessor)
                    subtract_total = subtract_total + subtract[predecessor]
                    predecessor = prev[predecessor]
                path.reverse() # Make list begin with 'start' node
                path_len = dist[end] - subtract_total
                return path, path_len

            neighbors = self.graph.get_neighbors(curr_node)
            for n in neighbors:
                if n in visited:
                    continue

                if self.use_elevation:
                    elev_diff = self.elevation(n) - self.elevation(curr_node)
                    heuristic_weight = max([0, elev_diff])
                    alt_path_weight = curr_dist + self.distance(curr_node, n) + heuristic_weight
                    subtract_this = heuristic_weight
                else:
                    alt_path_weight = curr_dist + self.distance(curr_node, n)
                    subtract_this = 0.

                if alt_path_weight < dist[n]:
                    dist[n] = alt_path_weight
                    subtract[n] = subtract_this
                    prev[n] = curr_node
                    heapq.heappush(priority_queue, (alt_path_weight, n))

        """
        Should we only allow a node to appear once in the priority queue? That would
        be memory-efficient, but requires us to do a linear search every time we
        want to update a node's priority queue value.
        """

        print("No path found")
        return [], math.inf

