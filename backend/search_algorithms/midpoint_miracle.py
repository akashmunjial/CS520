"""Contains a class used for finding an elevation-maximizing path.
"""
import math

from backend.search_algorithms.dijkstra import Dijkstra
from backend.search_algorithms.search_result import SearchResult
from backend.search_algorithms.search_algorithm import SearchAlgorithm
from backend.graph_providers.graph_provider import GraphProvider


class MidpointMiracle(SearchAlgorithm):
    """A novel search algorithm for finding an elevation-maximizing path.

    Simply put, this algorithm searches for an elevation-maximizing path by
    reducing the problem to one of finding an especially good intermediate
    node to have along the path from the start node to the end node.
    We refer to an intermediate node as a 'midpoint', though it need not be
    equidistant from the start and end nodes.

    Attributes:
        graph_provider: A GraphProvider to facilitate the search.
    """
    SS_NOT_COMPUTED_MSG = "We have not computed the single source data yet."

    def __init__(self, graph_provider):
        self.graph_provider = graph_provider
        self._single_source_data = None

    @property
    def graph_provider(self):
        return self._graph_provider

    @graph_provider.setter
    def graph_provider(self, graph_provider):
        if not isinstance(graph_provider, GraphProvider):
            raise ValueError(f"Graph provider must be a subclass of GraphProvider")
        self._graph_provider = graph_provider

    def _elevation(self, node):
        """Obtain the elevation of a given node.

        Args:
            node: The node whose elevation we want.

        Returns:
            The 'z' coordinate of the node, according to the graph provider.
        """
        return self.graph_provider.get_coords(node)['z']

    def _compute_single_source_data(self, start, end):
        """Run single-source Dijkstra to get shortest-paths info we need.

        We need to know shortest paths from start to every other node in the
        graph and from end to every other node in the graph so that for any
        given node, we can just concatenate two paths to get one that goes
        from start to end through that node. Modifies the MidpointMiracle's
        state in-place.

        Args:
            start: The start node for the full paths interest.
            end: The end node for the full paths of interest.
        """
        single_source_data = {}
        dijkstra = Dijkstra(self.graph_provider)
        single_source_data['start'] = dijkstra.single_source(start)
        single_source_data['end'] = dijkstra.single_source(end)

        self._single_source_data = single_source_data

    def _filter_func_factory(self, start, end, max_path_len):
        """Creates a function for filtering midpoint nodes.

        Args:
            start: The start node for paths of interest.
            end: The end node for paths of interest.
            max_path_len: The upper bound on acceptable path lengths.

        Returns:
            A function which can be used to filter candidate midpoint
            nodes along the path ultimately returned by the `search` method.
            For example, it will filter out nodes for whom the full path
            through that node (using paths from single-source step) is longer
            than max_path_len.

        Raises:
            An Exception if we have not yet computed the single source data.
        """
        if self._single_source_data is None:
            raise Exception(SS_NOT_COMPUTED_MSG)

        ele_start = self._elevation(start)
        ele_end = self._elevation(end)

        min_of_start_and_end = min([ele_start, ele_end])
        def dips_below_min(node):
            return self._elevation(node) < min_of_start_and_end

        dists_from_start = self._single_source_data['start']['dist']
        dists_to_end = self._single_source_data['end']['dist']
        def filter_func(node):
            # We are only interested in intermediate nodes
            #if node == start or node == end:
            #    return False

            # Filter out nodes for which full path through that node (using
            # paths from single-source step) is longer than maximum allowed
            dist_from_start = dists_from_start[node]
            dist_to_end = dists_to_end[node]
            if dist_from_start + dist_to_end > max_path_len:
                return False

            # Check that there is at least a hope of elevation gain
            if not dips_below_min(node) and self._elevation(node) < ele_start:
                return False

            return True

        return filter_func

    def _sort_func_factory(self, start, end):
        """Creates a function used for sorting candidate midpoints.

        In particular, we seek to sort them in terms of a lower bound on the
        elevation gain achievable by having that point on the path from start
        to end.

        Args:
            start: The start node for paths of interest.
            end: The end node for paths of interest.

        Returns:
            A function that takes in a node and returns a lower bound on the
            elevation gain achievable by having that node on our path. It can
            therefore be used straightforwardly to sort the candidate
            midpoints.
        """
        ele_start = self._elevation(start)
        ele_end = self._elevation(end)

        def sort_func(node):
            node_ele = self._elevation(node)
            # Potential elevation gain for path segment from start to node
            potential_gain_prefix = max([0., node_ele - ele_start])
            # Potential elevation gain for path segment from node to end
            potential_gain_suffix = max([0., ele_end - node_ele])
            return max([potential_gain_prefix, potential_gain_suffix])

        return sort_func

    def _select_and_prune(self, sorted_candidates, keep_n, prune_depth):
        """Given sorted candidate nodes, cleverly select high-quality ones.

        Args:
            keep_n: The maximum number of candidates to select. We may select
                fewer due to pruning or to the limited number of candidates.
            prune_depth: Each time we select a midpoint, remove from our pool
                of candidates in the next step of selection all nodes reachable
                by traversing this many edges starting from that midpoint.

        Returns:
            A list of at most 'keep_n' selected candidate midpoints.
        """
        selected_midpoints = []
        while(len(sorted_candidates) > 0 and len(selected_midpoints) < keep_n):
            curr = sorted_candidates.pop(0)
            selected_midpoints.append(curr)

            # Prune away neighbors so that we select a diverse set of midpoints
            if prune_depth > 0:
                pruned = set(self.graph_provider.get_neighbors(curr))
                old_neighbors = pruned
                for _ in range(prune_depth - 1):
                    new_neighbors = [n for node in old_neighbors for n in self.graph_provider.get_neighbors(node)]
                    new_neighbors = set(new_neighbors)
                    pruned = pruned.union(new_neighbors)
                    old_neighbors = new_neighbors
                sorted_candidates = [node for node in sorted_candidates if node not in pruned]

        return selected_midpoints

    def _reconstruct_result(self, node, ss_result, backward=False):
        """Reconstruct a path to or from a node using a single-source result.

        Args:
            node: The node for which we want to reconstruct the path either from
                the source of 'ss_result' to this node, or from this node to that
                source.
            ss_result: A result of single-source shortest paths search, for which
                we are trying to reconstruct the path from the source to 'node'
                or from 'node' to the source.
            backward: If False, we will reconstruct the path from the source of
                'ss_result' to 'node', else we will reconstruct the path from
                'node' to the source of 'ss_result'.

        Returns:
            A dict containing the path, path length, and elevation gain
            of the reconstructed path from the source of 'ss_result' to node
            (or from node to source if 'backward' is True), as well as data
            needed to merge results later on.
        """
        prev = ss_result['prev']
        ele_diff = ss_result['ele_diff']

        path = [node]
        ele_gain = 0.
        contributions = {} # Of each node, to the cumulative elevation gain
        dist = ss_result['dist']

        if backward:
            # 'node' is the start point and so does not contribute to ele_gain
            contributions[node] = 0.
        else:
            # The ele diff between 'node' (first on the path) and next node
            # on the path toward the source
            contributions[node] = max([0., ele_diff[node]])
        ele_gain += contributions[node]

        # Follow backpointers to reconstruct path and compute statistics
        successor = node
        curr_node = prev[node]
        while curr_node is not None:
            path.append(curr_node)
            if backward:
                # ele_diff's were computed moving forward toward 'node', so we
                # must be careful to get the right contribution here
                contribution = max([0., -ele_diff[successor]])
            else:
                contribution = max([0., ele_diff[curr_node]])
            contributions[curr_node] = contribution
            ele_gain += contributions[curr_node]
            curr_node = prev[curr_node]
            successor = curr_node

        # Since path was built by appending and backtracking, need to
        # reverse it if 'node' is supposed to be the terminus
        if not backward:
            path.reverse()

        # Not yet a SearchResult: more processing needed in merge step
        result = {
            'path': path,
            'path_len': dist[node],
            'ele_gain': ele_gain,
            'contributions': contributions,
            'dist': dist
        }

        return result

    def _merge_results(self, res_to_node, res_to_end):
        """Merges reconstructed results into one SearchResult from start to end.

        Essentially concatenates a path from the start node to midpoint with a
        path from the midpoint to the end node, but crucially ensures that the
        merged result is a SIMPLE path, i.e. that no nodes are repeated.

        Args:
            res_to_node: The reconstructed result from the start node to the
                midpoint.
            res_to_end: The reconstructed result from the midpoint to the
                end node.

        Returns:
            A SearchResult formed by merging the input results into a simple
            path from the start node to the end node, via the midpoint.
        """
        path_to_node = res_to_node['path']
        path_to_end = res_to_end['path']

        # Contains distances from start to other nodes
        dist_from_start = res_to_node['dist']
        # Contains distances from end to other nodes
        dist_from_end = res_to_end['dist']

        to_node_contributions = res_to_node['contributions']
        to_end_contributions = res_to_end['contributions']

        # Remove any shared nodes from the concatenated path
        shared_node = None
        i = 0
        full_path_ele_gain = res_to_node['ele_gain'] + res_to_end['ele_gain']
        while(i < len(path_to_end) and len(path_to_node) > 0
                and path_to_node[-1] == path_to_end[i]):
            shared_node = path_to_node[-1]
            path_to_node.pop(-1)
            full_path_ele_gain -= to_node_contributions[shared_node]
            full_path_ele_gain -= to_end_contributions[shared_node]
            i += 1
        # Replace the final shared node (midpoint if the paths share no other nodes)
        path_to_node.append(shared_node)
        full_path_ele_gain += to_node_contributions[shared_node]
        full_path = path_to_node + path_to_end[i:]
        full_path_len = dist_from_start[shared_node] + dist_from_end[shared_node]

        return SearchResult(
            path=full_path,
            path_len= full_path_len,
            ele_gain=full_path_ele_gain
        )

    def _obtain_full_result(self, midpoint):
        """Given a midpoint, reconstruct the full SearchResult via the midpoint.

        Args:
            midpoint: The node for which we will obtain the full
                SearchResult corresponding to the path from the start node
                to the end node via this node.

        Returns:
            A SearchResult corresponding to the path from the start node to
            the end node via 'midpoint'.

        Raises:
            An Exception if we have not computed the single-source data yet.
        """
        if self._single_source_data is None:
            raise Exception(SS_NOT_COMPUTED_MSG)
        ss_start = self._single_source_data['start']
        ss_end = self._single_source_data['end']

        res_to_midpoint = self._reconstruct_result(midpoint, ss_start, backward=False)
        res_to_end = self._reconstruct_result(midpoint, ss_end, backward=True)
        merged = self._merge_results(res_to_midpoint, res_to_end)

        return merged

    def search(self, start, end, max_path_len, keep_n=10, prune_depth=3):
        """Search for an elevation-maximizing path from 'start' to 'end'.

        Args:
            start: The start node of the path of interest.
            end: The end node of the path of interest.
            max_path_len: The maximum allowable length of a path.
            keep_n: Optional; an integer hyperparameter of the search used in
                the selection/pruning process. See '_select_and_prune' function.
            prune_depth: Optional; an integer hyperparameter of the search used in
                the selection/pruning process. See '_select_and_prune' function.

        Returns:
            A SearchResult corresponding to the best path we were able to
            find by analyzing potential midpoints and choosing the best among
            a small set of high-quality ones.
        """
        self._compute_single_source_data(start, end)

        # Filter and sort candidate midpoints
        filter_func = self._filter_func_factory(start, end, max_path_len)
        midpoint_candidates = filter(filter_func, self.graph_provider.get_all_nodes())
        sort_func = self._sort_func_factory(start, end)
        sorted_candidates = sorted(midpoint_candidates, key=sort_func, reverse=True)

        # Cleverly select some high-quality candidates and build full-path SearchResult's
        selected_midpoints = self._select_and_prune(sorted_candidates, keep_n, prune_depth)
        results = [self._obtain_full_result(midpoint) for midpoint in selected_midpoints]

        best_res = SearchResult(path=[], path_len=math.inf, ele_gain=-math.inf)
        for r in results:
            if r.ele_gain > best_res.ele_gain:
                best_res = r

        return best_res

