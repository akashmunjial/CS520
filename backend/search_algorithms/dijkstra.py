import math
from collections import defaultdict
from heapdict import heapdict

from backend.search_algorithms.search_result import SearchResult
from backend.search_algorithms.search_algorithm import SearchAlgorithm

'''
Essentially follows the implementation here: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue
'''
class Dijkstra(SearchAlgorithm):
    def __init__(self, graph_provider):
        self.graph_provider = graph_provider

    def __distance(self, node1, node2):
        return self.graph_provider.get_edge_distance(node1, node2)

    def __elevation(self, node):
        return self.graph_provider.get_coords(node)['z']

    def single_source(self, start):
        """One line sumamry.

        Some more stuff.

        Args:
            start: The start node (its integer id).

        Returns:
            A dict mapping stuff.
        """
        prev = defaultdict(lambda: None)
        dist = defaultdict(lambda: math.inf) # The weight of the current minimum-weight path to a node
        ele_diff = {}
        visited = set()
        priority_queue = heapdict()

        prev[start] = None
        dist[start] = 0.
        ele_diff[start] = 0.
        priority_queue[start] = dist[start]
        while len(priority_queue) > 0:
            curr_node, curr_dist = priority_queue.popitem()
            visited.add(curr_node)
            neighbors = list(self.graph_provider.get_neighbors(curr_node))
            for n in neighbors:
                if n in visited:
                    continue
                alt_path_dist = dist[curr_node] + self.__distance(curr_node, n)
                curr_ele_diff = self.__elevation(n) - self.__elevation(curr_node)
                if alt_path_dist < dist[n]:
                    ele_diff[n] = curr_ele_diff
                    dist[n] = alt_path_dist
                    prev[n] = curr_node
                    priority_queue[n] = dist[n]

        result = {
            'prev': prev,
            'dist': dist,
            'ele_diff': ele_diff
        }

        return result

    def search(self, start, end, max_path_len=math.inf, backward=False):
        minimize_ele = max_path_len < math.inf

        prev = {}
        dist = {}
        weight = defaultdict(lambda: math.inf) # The weight of the current minimum-weight path to a node
        ele_diff = {}
        visited = set()
        priority_queue = heapdict()

        ele_start = self.__elevation(start)
        ele_end = self.__elevation(end)

        prev[start] = None
        dist[start] = 0.
        weight[start] = 0.
        ele_diff[start] = 0.
        priority_queue[start] = weight[start]
        while len(priority_queue) > 0:
            curr_node, curr_weight = priority_queue.popitem()

            '''Mark as visited, which implies dist[curr_node] currently
            contains shortest distance between 'start' and 'curr_node'
            '''
            visited.add(curr_node)
            if curr_node == end:
                path = [end]
                predecessor = prev[end]
                cum_ele_diff = 0.
                while predecessor is not None:
                    path.append(predecessor)
                    if backward:
                        cum_ele_diff += max([0., -ele_diff[predecessor]])
                    else:
                        cum_ele_diff += max([0., ele_diff[predecessor]])
                    predecessor = prev[predecessor]
                if not backward:
                    path.reverse() # Make list begin with 'start' node
                path_len = dist[end]
                return SearchResult(path, path_len, cum_ele_diff)


            neighbors = list(self.graph_provider.get_neighbors(curr_node))

            for i, n in enumerate(neighbors):
                if n in visited:
                    continue

                alt_path_dist = dist[curr_node] + self.__distance(curr_node, n)
                ele_n = self.__elevation(n)
                curr_ele_diff = ele_n - self.__elevation(curr_node)
                if minimize_ele:
                    heuristic_weight = max([0., curr_ele_diff])
                    alt_path_weight = curr_weight + heuristic_weight
                else:
                    alt_path_weight = alt_path_dist

                if alt_path_dist <= max_path_len:
                    if alt_path_weight < weight[n]:
                        ele_diff[n] = curr_ele_diff
                        dist[n] = alt_path_dist
                        weight[n] = alt_path_weight
                        prev[n] = curr_node
                        priority_queue[n] = weight[n]

        return SearchResult()
