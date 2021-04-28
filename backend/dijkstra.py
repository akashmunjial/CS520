import math
from collections import defaultdict
import scipy #XXX
import osmnx #XXX
import numpy as np
from heapdict import heapdict

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

    def single_source(self, start):
        prev = defaultdict(lambda: None) # The weight of the current minimum-weight path to a node
        dist = defaultdict(lambda: math.inf) # The weight of the current minimum-weight path to a node
        elev_diff = {}
        visited = set()
        priority_queue = heapdict()

        prev[start] = None
        dist[start] = 0.
        elev_diff[start] = 0.
        priority_queue[start] = dist[start]
        while len(priority_queue) > 0:
            curr_node, curr_dist = priority_queue.popitem()

            visited.add(curr_node)

            neighbors = list(self.graph_provider.get_neighbors(curr_node))
            for n in neighbors:
                if n in visited:
                    continue

                alt_path_dist = dist[curr_node] + self.distance(curr_node, n)
                curr_elev_diff = self.elevation(n) - self.elevation(curr_node)

                if alt_path_dist < dist[n]:
                    elev_diff[n] = curr_elev_diff
                    dist[n] = alt_path_dist
                    prev[n] = curr_node
                    priority_queue[n] = dist[n]

        result = {
                'prev': prev,
                'dist': dist,
                'elev_diff': elev_diff
                }

        return result

    def search(self, start, end, use_elevation=False, max_path_len=math.inf, visualize=False, backward=False):
        if use_elevation:
            assert max_path_len != math.inf, "If we want to use elevation data, we need a finite maximum path length we cannot exceed"

        result = {
                'path': [],
                'path_len': math.inf,
                'ele_gain': math.inf, # Assuming opt goal is minimize, this makes sense as default so that we never take an empty path as best_result
                }

        prev = {}
        dist = {}
        weight = defaultdict(lambda: math.inf) # The weight of the current minimum-weight path to a node
        elev_diff = {}
        visited = set()
        priority_queue = heapdict()

        ele_start = self.elevation(start)
        ele_end = self.elevation(end)
        #print(f"Ele start: {ele_start}")
        #print(f"Ele end: {ele_end}")
        max_ele = max([ele_start, ele_end])

        prev[start] = None
        dist[start] = 0.
        weight[start] = 0.
        elev_diff[start] = 0.
        priority_queue[start] = weight[start]
        while len(priority_queue) > 0:
            curr_node, curr_weight = priority_queue.popitem()

            '''Mark as visited, which implies dist[curr_node] currently
            contains shortest distance between 'start' and 'curr_node'
            '''
            visited.add(curr_node)
            if curr_node == end:
                #print(sorted([dist[n] for n in visited]))
                print(f"And finally, dist to end is {dist[end]}")
                if visualize:
                    if use_elevation:
                        osmnx.plot.plot_graph(self.graph_provider.graph.subgraph(list(visited)))
                    else:
                        osmnx.plot.plot_graph(self.graph_provider.graph)
                print(f"Highest ele seen: {max_ele}")
                path = [end]
                predecessor = prev[end]
                cum_elev_diff = 0.
                while predecessor is not None:
                    path.append(predecessor)
                    if backward:
                        cum_elev_diff += max([0., -elev_diff[predecessor]])
                    else:
                        cum_elev_diff += max([0., elev_diff[predecessor]])
                    predecessor = prev[predecessor]
                if not backward:
                    path.reverse() # Make list begin with 'start' node
                path_len = dist[end]
                print(f"Cum elev diff: {cum_elev_diff}")
                result['path'] = path
                result['path_len'] = path_len
                result['ele_gain'] = cum_elev_diff
                return result

            neighbors = list(self.graph_provider.get_neighbors(curr_node))

            for i, n in enumerate(neighbors):
                if n in visited:
                    continue

                alt_path_dist = dist[curr_node] + self.distance(curr_node, n)
                ele_n = self.elevation(n)
                max_ele = max([max_ele, ele_n])
                curr_elev_diff = ele_n - self.elevation(curr_node)
                if use_elevation:
                    heuristic_weight = max([0., curr_elev_diff])
                    alt_path_weight = curr_weight + heuristic_weight
                else:
                    alt_path_weight = alt_path_dist

                if alt_path_dist <= max_path_len:
                    if alt_path_weight < weight[n]:
                        elev_diff[n] = curr_elev_diff
                        dist[n] = alt_path_dist
                        weight[n] = alt_path_weight
                        prev[n] = curr_node
                        priority_queue[n] = weight[n]

        print("No path found")
        if visualize:
            if use_elevation:
                osmnx.plot.plot_graph(self.graph_provider.graph.subgraph(list(visited)))
            else:
                osmnx.plot.plot_graph(self.graph_provider.graph)

        return result

#if use_elevation:
            #if False:
            #    softmax_list = []
            #    for n in neighbors:
            #        if n is visited:
            #            continue
            #        ele_n = self.elevation(n)
            #        curr_elev_diff = ele_n - self.elevation(curr_node)
            #        hinge_diff = max([0., curr_elev_diff])
            #        if opt_goal == 'minimal':
            #            softmax_list.append(hinge_diff)
            #        else:
            #            softmax_list.append(-hinge_diff)
            #    #softmax = 2 ** np.array(softmax_list)
            #    softmax = 3 ** np.array(softmax_list)
            #    #softmax = softmax / np.sum(softmax)

