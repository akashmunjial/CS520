from math import inf

from backend.search_algs.dijkstra import Dijkstra
from backend.search_algs.search_result import SearchResult

SS_NOT_COMPUTED_MSG = "We have not computed the single source data yet."

class MidpointMiracle:

    def __init__(self, graph_provider):
        self.graph_provider = graph_provider
        self._single_source_data = None

    def __elevation(self, node):
        return self.graph_provider.get_coords(node)['z']

    def __compute_single_source_data(self, start, end):
        single_source_data = {}
        dijkstra = Dijkstra(self.graph_provider)
        single_source_data['start'] = dijkstra.single_source(start)
        single_source_data['end'] = dijkstra.single_source(end)

        self._single_source_data = single_source_data

    def __filter_func_factory(self, start, end, max_path_len):
        assert self._single_source_data is not None, SS_NOT_COMPUTED_MSG
        ele_start = self.__elevation(start)
        ele_end = self.__elevation(end)

        min_of_start_and_end = min([ele_start, ele_end])
        def dips_below_min(node):
            return self.__elevation(node) < min_of_start_and_end

        dists_from_start = self._single_source_data['start']['dist']
        dists_to_end = self._single_source_data['end']['dist']
        def filter_func(node):
            if node == start or node == end:
                return False

            dist_to_start = dists_from_start[node]
            dist_to_end = dists_to_end[node]
            if dist_to_start + dist_to_end > max_path_len:
                return False

            # Check that there is at least a hope of elevation gain here
            if not dips_below_min(node) and self.__elevation(node) < ele_start:
                return False

            return True

        return filter_func

    def __sort_func_factory(self, start, end):
        ele_start = self.__elevation(start)
        ele_end = self.__elevation(end)

        def sort_func(node):
            node_ele = self.__elevation(node)
            potential_gain_prefix = max([0., node_ele - ele_start])
            potential_gain_suffix = max([0., ele_end - node_ele])
            #if node_ele < ele_start:
            #    # We will gain at least this much while traveling
            #    # from node to end
            #    value = max([0., ele_end - node_ele])
            #else:
            #    # We will gain at least this much by traveling from
            #    # start to node
            #    value = node_ele - ele_start
            return max([potential_gain_prefix, potential_gain_suffix])

        return sort_func

    def __merge_results(self, res_to_node, res_to_end):
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

        # Handle path differently
        return SearchResult(
            path=path_to_node + path_to_end[i:],
            path_len=dist_prefix[shared_node] + dist_suffix[shared_node],
            ele_gain=res_to_node['ele_gain'] + res_to_end['ele_gain'] - sub_from_gain
        )

    def __reconstruct_result(self, end, ss_result, backward=False):
            prev = ss_result['prev']
            ele_diff = ss_result['ele_diff']
            dist = ss_result['dist']

            path = [end]
            # For forward direction, this is the diff between the second-to-last-node and 'end'
            # but for backward direction, this is the diff between 'end', which is really the start, and the second node on the path
            #end_contribution = max([0., -ele_diff[end]]) if backward else max([0., ele_diff[end]])
            end_contribution = 0. if backward else max([0., ele_diff[end]])
            cum_ele_diff = end_contribution
            successor = end
            curr_node = prev[end]
            contributions = {} # To cumulative elevation gain
            contributions[end] = end_contribution
            while curr_node is not None:
                path.append(curr_node)
                if backward:
                    # contribution should be ele_diff of the successor
                    contribution = max([0., -ele_diff[successor]])
                else:
                    contribution = max([0., ele_diff[curr_node]])
                cum_ele_diff += contribution
                contributions[curr_node] = contribution
                curr_node = prev[curr_node]
                successor = curr_node

            if not backward:
                path.reverse() # Make list begin with 'start' node

            path_len = dist[end]

            result = {
                'path': path,
                'path_len': path_len,
                'ele_gain': cum_ele_diff,
                'contributions': contributions,
                'dist': dist
            }

            return result

    def __select_and_prune(self, sorted_candidates, keep_n, prune_depth):
        # Keep just a few of the potential midpoints, and each time we select
        # a midpoint, prune away it's neighbors so we get more diverse points
        selected_midpoints = []
        while(len(sorted_candidates) > 0 and len(selected_midpoints) < keep_n):
            curr = sorted_candidates.pop(0)
            selected_midpoints.append(curr)

            # Pruning
            if prune_depth > 0:
                neighbors = set(self.graph_provider.get_neighbors(curr))
                old_neighbors = neighbors
                for _ in range(prune_depth - 1):
                    new_neighbors = [n for node in old_neighbors for n in self.graph_provider.get_neighbors(node)]
                    new_neighbors = set(new_neighbors)
                    neighbors = neighbors.union(new_neighbors)
                    old_neighbors = new_neighbors
                sorted_candidates = [node for node in sorted_candidates if node not in neighbors]
        return selected_midpoints

    def __obtain_full_result(self, midpoint):
        assert self._single_source_data is not None, SS_NOT_COMPUTED_MSG
        ss_start = self._single_source_data['start']
        ss_end = self._single_source_data['end']

        res_to_midpoint = self.__reconstruct_result(midpoint, ss_start, backward=False)
        res_to_end = self.__reconstruct_result(midpoint, ss_end, backward=True)
        merged = self.__merge_results(res_to_midpoint, res_to_end)

        return merged

    def search(self, start, end, max_path_len, keep_n=10, prune_depth=3):
        self.__compute_single_source_data(start, end)

        filter_func = self.__filter_func_factory(start, end, max_path_len)
        midpoint_candidates = filter(filter_func, self.graph_provider.get_all_nodes())

        sort_func = self.__sort_func_factory(start, end)
        sorted_candidates = sorted(midpoint_candidates, key=sort_func, reverse=True)

        selected_midpoints = self.__select_and_prune(sorted_candidates, keep_n, prune_depth)

        results = [self.__obtain_full_result(midpoint) for midpoint in selected_midpoints]

        best_res = SearchResult(path=[], path_len=inf, ele_gain=-inf)
        for r in results:
            if r.ele_gain > best_res.ele_gain:
                best_res = r
        #best_result = max(results, key=lambda r: r.ele_gain)

        return best_res

