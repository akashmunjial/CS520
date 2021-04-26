import heapq
import math
from collections import defaultdict
import scipy #XXX
import osmnx #XXX
import numpy as np

'''
Essentially follows the implementation here: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue
'''
class Dijkstra:
    def __init__(self, graph_provider):
        self.graph_provider = graph_provider

    def distance(self, node1, node2):
        return self.graph_provider.get_edge_distance(node1, node2)

    def elevation(self, node):
        return self.graph_provider.get_coords(node)['z']

    def search(self, start, end, use_elevation=False, max_path_len=math.inf, opt_goal='maximal', alpha=0.9):
        assert alpha >= 0. and alpha <= 1.
        if use_elevation:
            assert max_path_len != math.inf, "If we want to use elevation data, we need a finite maximum path length we cannot exceed"
            assert opt_goal == 'maximal' or opt_goal == 'minimal'

        prev = {}
        dist = {}
        weight = defaultdict(lambda: math.inf) # The weight of the current minimum-weight path to a node
        elev_diff = {}
        visited = set()
        priority_queue = []
        #subtract = {}

        ele_start = self.elevation(start)
        ele_end = self.elevation(end)
        print(f"Ele start: {ele_start}")
        print(f"Ele end: {ele_end}")
        max_ele = max([ele_start, ele_end])

        prev[start] = None
        dist[start] = 0.
        weight[start] = 0.
        elev_diff[start] = 0.
        heapq.heappush(priority_queue, (weight[start], start))
        while len(priority_queue) > 0:
            curr_weight, curr_node = heapq.heappop(priority_queue)

            '''Mark as visited, which implies dist[curr_node] currently
            contains shortest distance between 'start' and 'curr_node'
            '''
            visited.add(curr_node)
            if curr_node == end:
                print(sorted([dist[n] for n in visited]))
                print(f"And finally, dist to end is {dist[end]}")
                #osmnx.plot.plot_graph(self.graph_provider.graph)
                #osmnx.plot.plot_graph(self.graph_provider.graph.subgraph(list(visited)))
                print(f"Highest ele seen: {max_ele}")
                path = [end]
                predecessor = prev[end]
                cum_elev_diff = 0.
                while predecessor is not None:
                    path.append(predecessor)
                    cum_elev_diff += max([0., elev_diff[predecessor]])
                    predecessor = prev[predecessor]
                path.reverse() # Make list begin with 'start' node
                path_len = dist[end]
                print(f"Cum elev diff: {cum_elev_diff}")
                return path, path_len

            neighbors = list(self.graph_provider.get_neighbors(curr_node))
            if use_elevation:
                softmax_list = []
                for n in neighbors:
                    if n is visited:
                        continue
                    softmax_list.append(-self.elevation(n))
                softmax = np.array(softmax_list) ** 3
                softmax = softmax / np.sum(softmax)
                print(f"Dist: {softmax}")

            for i, n in enumerate(neighbors):
                if n in visited:
                    continue

                alt_path_dist = dist[curr_node] + self.distance(curr_node, n)
                ele_n = self.elevation(n)
                max_ele = max([max_ele, ele_n])
                curr_elev_diff = ele_n - self.elevation(curr_node)
                if use_elevation:
                    #print(f"Elev_diff: {elev_diff}")
                    if opt_goal == 'minimal':
                        heuristic_weight = max([0., curr_elev_diff])
                        if heuristic_weight > 0.:
                            pass
                            #heuristic_weight += 1.
                            #heuristic_weight
                        #print(f"Heuristic weight is {heuristic_weight}")
                        alt_path_weight = curr_weight + self.distance(curr_node, n) + heuristic_weight
                    else:
                        heuristic_weight = max([0., curr_elev_diff])
                        #heuristic_weight = math.exp(-heuristic_weight)
                        heuristic_weight = 5. ** (-heuristic_weight)
                        #alt_path_weight = curr_weight + softmax[i] * self.distance(curr_node, n)
                        alt_path_weight = curr_weight + heuristic_weight
                else:
                    alt_path_weight = alt_path_dist

                if alt_path_weight < weight[n] and alt_path_dist < max_path_len:
                    elev_diff[n] = curr_elev_diff
                    dist[n] = alt_path_dist
                    weight[n] = alt_path_weight
                    prev[n] = curr_node
                    heapq.heappush(priority_queue, (weight[n], n))

        """
        Should we only allow a node to appear once in the priority queue? That would
        be memory-efficient, but requires us to do a linear search every time we
        want to update a node's priority queue value.
        """

        print("No path found")
        return [], math.inf

