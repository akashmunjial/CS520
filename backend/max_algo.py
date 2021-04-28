import math
from collections import defaultdict
import scipy #XXX
import osmnx #XXX
import numpy as np
from heapdict import heapdict
from backend.dijkstra import Dijkstra

'''
Essentially follows the implementation here: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue
'''
class MaxSearch:
    def __init__(self, graph_provider):
        self.graph_provider = graph_provider

    def distance(self, node1, node2):
        return self.graph_provider.get_edge_distance(node1, node2)

    def crow_flies(self, node1, node2):
        coords1 = self.graph_provider.get_coords(node1)
        x1, y1 = coords1['x'], coords1['y']
        coords2 = self.graph_provider.get_coords(node2)
        x2, y2 = coords2['x'], coords2['y']
        dist = osmnx.distance.great_circle_vec(y1,x1,y2,x2)
        return dist

    def elevation(self, node):
        return self.graph_provider.get_coords(node)['z']

    def search(self, start, end, max_path_len=math.inf, visualize=False, backward=False):
        result = {
                'path': [],
                'path_len': math.inf,
                'ele_gain': -math.inf, # Assuming opt goal is minimize, this makes sense as default so that we never take an empty path as best_result
                }

        # Single-source shortest paths to all nodes
        #print("\nBegin single source")
        #ss_dijkstra = Dijkstra(self.graph_provider)
        #ss_start_prev, ss_start_dist, ss_start_elev_diff = ss_dijkstra.single_source(start)
        #ss_end_prev, ss_end_dist, ss_end_elev_diff = ss_dijkstra.single_source(end)
        #print("End single source\n")

        all_nodes = self.graph_provider.graph.nodes

        ele_start = self.elevation(start)
        ele_end = self.elevation(end)

        min_of_start_and_end = min([ele_start, ele_end])
        def dips_below_min(node):
            return self.elevation(node) < min_of_start_and_end

        def is_acceptable(node):
            ele_end = self.elevation(end)
            if node == start or node == end:
                return False

            acceptable_range = max_path_len
            dist_to_start = self.crow_flies(start, node)
            #dist_to_start = ss_start_dist[node]
            dist_to_end = self.crow_flies(end, node)
            #dist_to_end = ss_end_dist[node]
            # Check if close enough to start or end
            if (dist_to_start > acceptable_range
                    and dist_to_end > acceptable_range):
                return False

            # Check that there is at least a hope of path being
            # less or equal max_path_len
            if dist_to_start + dist_to_end > 0.7 * max_path_len:
                return False

            # Check that there is at least a hope of elevation gain here
            if not dips_below_min(node) and self.elevation(node) < ele_start:
                return False

            return True

        acceptable_nodes = [node for node in all_nodes if is_acceptable(node)]
        print(f"\nThere were {len(acceptable_nodes)} acceptable nodes\n")

        sorted_nodes = sorted(
                acceptable_nodes, key=lambda x: self.elevation(x), reverse=True)

        keep_n = 10
        prune_depth = 3
        keep = []
        while(len(sorted_nodes) > 0 and len(keep) < keep_n):
            curr = sorted_nodes.pop(0)
            keep.append(curr)
            neighbors = set(self.graph_provider.get_neighbors(curr))
            old_neighbors = neighbors
            for _ in range(prune_depth - 1):
                new_neighbors = [n for node in old_neighbors for n in self.graph_provider.get_neighbors(node)] 
                new_neighbors = set(new_neighbors)
                neighbors = neighbors.union(new_neighbors)
                old_neighbors = new_neighbors
            # Expensive: probably an easier way to do this
            sorted_nodes = [node for node in sorted_nodes if node not in neighbors]

        print(f"\nThere were {len(keep)} kept\n")

        def merge_results(res_to_node, res_to_end):
            path_to_node = res_to_node['path']
            path_to_end = res_to_end['path']
            # Might have to deal with repeated nodes in the path
            # in a clever way here...
            first_shared = None
            i = 0
            while(path_to_node[-1] == path_to_end[i]):
                shared_node = path_to_node[-1]
                path_to_node.pop(-1)
                i += 1
            assert len(set(path_to_node).intersection(set(path_to_end))) == 0
            path_to_node.append(shared_node)

            merged = {}
            for k in res_to_node.keys():
                merged[k] = res_to_node[k] + res_to_end[k]
            merged['path'] = path_to_node + path_to_end[i:]

            return merged

        # Now get shortest paths to each of the keeps, and select the best path
        dijkstra = Dijkstra(self.graph_provider)
        best_res = result
        for node in keep:
            res_to_node = dijkstra.search(start, node)
            res_to_end = dijkstra.search(node, end)
            merged = merge_results(res_to_node, res_to_end)

            if merged['path_len'] <= max_path_len:
                if merged['ele_gain'] > best_res['ele_gain']:
                    best_path_to_node = res_to_node['path']
                    best_path_to_end = res_to_end['path']
                    best_res = merged

        #import pdb; pdb.set_trace()
        return best_res


    #def old_search(self, start, end, max_path_len=math.inf, visualize=False, backward=False):
    #    prev = {}
    #    dist = {}
    #    weight = defaultdict(lambda: math.inf) # The weight of the current minimum-weight path to a node
    #    elev_diff = {}
    #    visited = set()
    #    priority_queue = heapdict()
    #    stats = {
    #            'max_ele_diff': -math.inf,
    #            }

    #    result = {
    #            'path': [],
    #            'path_len': math.inf,
    #            'ele_gain': -math.inf, 
    #            }


    #    ele_start = self.elevation(start)
    #    ele_end = self.elevation(end)
    #    max_ele = max([ele_start, ele_end])

    #    prev[start] = None
    #    dist[start] = 0.
    #    weight[start] = 0.
    #    elev_diff[start] = 0.
    #    priority_queue[start] = weight[start]

    #    all_elev_diffs = [0.]
    #    all_dist_diffs = [0.]
    #    alpha = 0.
    #    #alpha_limit = (2/3) * self.graph_provider._n_nodes
    #    #alpha_limit = (2/3) * max_path_len
    #    alpha_limit = max_path_len
    #    print(f"alpha limit is {alpha_limit}")
    #    while len(priority_queue) > 0:
    #        curr_node, curr_weight = priority_queue.popitem()

    #        '''Mark as visited, which implies dist[curr_node] currently
    #        contains shortest distance between 'start' and 'curr_node'
    #        '''
    #        if curr_node in visited:
    #            continue
    #        visited.add(curr_node)
    #        if curr_node == end:
    #            if visualize:
    #                osmnx.plot.plot_graph(self.graph_provider.graph.subgraph(list(visited)))
    #                #osmnx.plot.plot_graph(self.graph_provider.graph)

    #            stats['Avg ele diff'] = np.mean(all_elev_diffs)
    #            stats['Median ele diff'] = np.median(all_dist_diffs)
    #            stats['Avg dist diff'] = np.mean(all_dist_diffs)
    #            stats['Median dist diff'] = np.median(all_dist_diffs)
    #            print_stats(stats)

    #            path = [end]
    #            predecessor = prev[end]
    #            cum_elev_diff = 0.
    #            while predecessor is not None:
    #                path.append(predecessor)
    #                if backward:
    #                    cum_elev_diff += max([0., -elev_diff[predecessor]])
    #                else:
    #                    cum_elev_diff += max([0., elev_diff[predecessor]])
    #                predecessor = prev[predecessor]

    #            if not backward:
    #                path.reverse() # Make list begin with 'start' node

    #            path_len = dist[end]
    #            result['path'] = path
    #            result['path_len'] = path_len
    #            result['ele_gain'] = cum_elev_diff
    #            return result

    #        neighbors = list(self.graph_provider.get_neighbors(curr_node))

    #        #alpha = min([1., len(visited) / alpha_limit])
    #        alpha = min([1., dist[curr_node] / alpha_limit])
    #        #alpha = 1.
    #        for n in neighbors:
    #            if n in visited:
    #                continue
    #            dist_to_n = self.distance(curr_node, n)
    #            all_dist_diffs.append(dist_to_n)
    #            alt_path_dist = dist[curr_node] + dist_to_n

    #            # In other words, how much farther away do we go from end by traveling to n?
    #            #delta_dist_from_end = self.distance(n, end) - self.distance(curr, end)
    #            #delta_dist_from_end = self.crow_flies(curr_node, end) - self.crow_flies(n, end) # Will be negative if going to n takes us farther away
    #            #all_dist_diffs.append(delta_dist_from_end)

    #            ele_n = self.elevation(n)
    #            max_ele = max([max_ele, ele_n])
    #            curr_elev_diff = ele_n - self.elevation(curr_node)
    #            stats['max_ele_diff'] = max([curr_elev_diff, stats['max_ele_diff']])
    #            all_elev_diffs.append(curr_elev_diff)

    #            heuristic_weight = 0.
    #            #weight_comp_a = alpha * -max([0., curr_elev_diff])
    #            #weight_comp_b = (1. - alpha) * dist_to_n
    #            weight_comp_a = -max([0., curr_elev_diff])
    #            weight_comp_b = alpha * dist_to_n # That is, as we get closer to the "edge", we weight distance more strongly
    #            heuristic_weight += weight_comp_a
    #            #heuristic_weight += weight_comp_b
    #            #heuristic_weight = -max([0., curr_elev_diff])
    #            alt_path_weight = curr_weight + heuristic_weight

    #            if alt_path_dist <= max_path_len:
    #                if alt_path_weight < weight[n]: # Why is this so crucial?
    #                    elev_diff[n] = curr_elev_diff
    #                    dist[n] = alt_path_dist
    #                    weight[n] = alt_path_weight
    #                    prev[n] = curr_node
    #                    #print(f"Pushing: {weight[n]}")
    #                    priority_queue[n] = weight[n]

    #    print("No path found")
    #    if visualize:
    #        osmnx.plot.plot_graph(self.graph_provider.graph.subgraph(list(visited)))
    #        #osmnx.plot.plot_graph(self.graph_provider.graph)

    #    return result


def print_stats(stats):
    print("\n====PRINTING STATS====")
    for k, v in stats.items():
        print(f"{k} is {v}")
    print("====END OF STATS====\n")
