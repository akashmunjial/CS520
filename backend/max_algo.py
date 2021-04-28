import math
import time
from collections import defaultdict
import scipy #XXX
import osmnx #XXX
import numpy as np
from heapdict import heapdict
from backend.dijkstra import Dijkstra

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
        start_time = time.time()
        ss_dijkstra = Dijkstra(self.graph_provider)
        ss_result_start = ss_dijkstra.single_source(start)
        ss_result_end = ss_dijkstra.single_source(end)
        end_time = time.time()
        print(f"Single source took (seconds): {end_time - start_time}\n")

        all_nodes = self.graph_provider.graph.nodes

        ele_start = self.elevation(start)
        ele_end = self.elevation(end)

        min_of_start_and_end = min([ele_start, ele_end])
        max_of_start_and_end = max([ele_start, ele_end])
        ss_start_dist = ss_result_start['dist']
        ss_end_dist = ss_result_end['dist']
        def dips_below_min(node):
            return self.elevation(node) < min_of_start_and_end

        def is_acceptable(node):
            ele_end = self.elevation(end)
            if node == start or node == end:
                return False

            acceptable_range = max_path_len
            dist_to_start = ss_start_dist[node]
            dist_to_end = ss_end_dist[node]

            # Check that there is at least a hope of path being
            # less or equal max_path_len
            if dist_to_start + dist_to_end > max_path_len:
                return False

            # Check that there is at least a hope of elevation gain here
            if not dips_below_min(node) and self.elevation(node) < ele_start:
                return False

            return True

        acceptable_nodes = [node for node in all_nodes if is_acceptable(node)]
        #print(f"\nThere were {len(acceptable_nodes)} acceptable nodes\n")

        def sort_func(node):
            node_elev = self.elevation(node)
            if node_elev < ele_start:
                # We will gain at least this much while traveling
                # from node to end
                value = max([0., ele_end - node_elev])
            else:
                # We will gain at least this much by traveling from
                # start to node
                value = node_elev - ele_start
            return value

        sorted_nodes = sorted(
                acceptable_nodes, key=sort_func, reverse=True)
        #sorted_nodes = sorted(
        #        acceptable_nodes, key=lambda x: self.elevation(x), reverse=True)

        # Keep just a few of the potential midpoints, and each time we select
        # a midpoint, prune away it's neighbors so we get more diverse points
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

        #print(f"\nThere were {len(keep)} kept\n")

        def merge_results(res_to_node, res_to_end):
            path_to_node = res_to_node['path']
            path_to_end = res_to_end['path']

            # Contains distances from start to midpoint
            dist_prefix = res_to_node['dist']
            # Contains distances from end to midpoint
            dist_suffix = res_to_end['dist']

            to_node_contributions = res_to_node['contributions']
            to_end_contributions = res_to_end['contributions']

            midpoint = path_to_node[-1]
            assert midpoint == path_to_end[0]

            # Remove any shared nodes from the concatenated path
            shared_node = None
            i = 0
            sub_from_gain = 0.
            while(i < len(path_to_end) and len(path_to_node) > 0 and path_to_node[-1] == path_to_end[i]):
                shared_node = path_to_node[-1]
                path_to_node.pop(-1)
                sub_from_gain += to_node_contributions[shared_node]
                sub_from_gain += to_end_contributions[shared_node]
                i += 1
            assert len(set(path_to_node).intersection(set(path_to_end))) == 0
            # Replace the final shared node (midpoint if the paths share no other nodes)
            path_to_node.append(shared_node)
            sub_from_gain -= to_node_contributions[shared_node]

            merged = {}
            # Handle path differently
            merged['path'] = path_to_node + path_to_end[i:]
            merged['path_len'] = dist_prefix[shared_node] + dist_suffix[shared_node]
            merged['ele_gain'] = res_to_node['ele_gain'] + res_to_end['ele_gain'] - sub_from_gain

            return merged

        def reconstruct_result(end, ss_result, backward=False):
            prev = ss_result['prev']
            elev_diff = ss_result['elev_diff']
            dist = ss_result['dist']

            path = [end]
            end_contribution = 0. if backward else max([0., elev_diff[end]])
            cum_elev_diff = end_contribution
            predecessor = prev[end]
            contributions = {} # To cumulative elevation gain
            contributions[end] = end_contribution
            while predecessor is not None:
                path.append(predecessor)
                if backward:
                    contribution = max([0., -elev_diff[predecessor]])
                else:
                    contribution = max([0., elev_diff[predecessor]])
                cum_elev_diff += contribution
                contributions[predecessor] = contribution
                predecessor = prev[predecessor]

            if not backward:
                path.reverse() # Make list begin with 'start' node
            path_len = dist[end]

            result = {
                    'path': path,
                    'path_len': path_len,
                    'ele_gain': cum_elev_diff,
                    'contributions': contributions,
                    'dist': dist
                    }

            return result


        # Now get shortest paths to each of the keeps, and select the best path
        best_res = result
        for node in keep:
            res_to_node = reconstruct_result(node, ss_result_start, backward=False)
            res_to_end = reconstruct_result(node, ss_result_end, backward=True)
            merged = merge_results(res_to_node, res_to_end)

            if merged['path_len'] <= max_path_len:
                if merged['ele_gain'] > best_res['ele_gain']:
                    best_path_to_node = res_to_node['path']
                    best_path_to_end = res_to_end['path']
                    best_res = merged

        print(f"\nTook another {time.time() - end_time} seconds to finish processing\n")
        return best_res
