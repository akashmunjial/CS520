"""Contains a class implementing two versions of search with Dijkstra.
"""
import math
from collections import defaultdict
from heapdict import heapdict

from backend.search_algorithms.search_result import SearchResult
from backend.search_algorithms.search_algorithm import SearchAlgorithm
from backend.graph_providers.graph_provider import GraphProvider


class Dijkstra(SearchAlgorithm):
    """The Dijkstra search algorithm, with two options for searching.

    We implement the single-source shortest paths version of Dijkstra
    which gets all shortest paths starting from a source, as well as the
    simpler form of Dijkstra which terminates once the path from the source
    to some target node has been found.

    Attributes:
        graph_provider: A GraphProvider to facilitate the search.
    """
    def __init__(self, graph_provider):
        self.graph_provider = graph_provider

    @property
    def graph_provider(self):
        return self._graph_provider

    @graph_provider.setter
    def graph_provider(self, graph_provider):
        if not isinstance(graph_provider, GraphProvider):
            raise ValueError(f"Graph provider must be a subclass of GraphProvider")
        self._graph_provider = graph_provider

    def _distance(self, node1, node2):
        """Obtain the distance between nodes.

        Args:
            node1: Tail node in the directed edge.
            node2: Head node in the directed edge.

        Returns:
            The distance between nodes, taken to be the length of the
            directed edge connecting them.
        """
        return self.graph_provider.get_edge_distance(node1, node2)

    def _elevation(self, node):
        """Obtain the elevation of a given node.

        Args:
            node: The node whose elevation we want.

        Returns:
            The 'z' coordinate of the node, according to the graph provider.
        """
        return self.graph_provider.get_coords(node)['z']

    def single_source(self, start):
        """Perform a single-source shortest paths search on the graph.

        Args:
            start: The source node for the search.

        Returns:
            A dict containing three mappings fully describing the results
            of the search in terms of backpointers, distances, and elevation
            differences.
        """
        # A mapping from nodes to backpointers for reconstructing paths
        self._prev = defaultdict(lambda: None)
        # The distance of the current minimum-distance path to a node
        self._dist = defaultdict(lambda: math.inf)
        # Map a node 'n' to the (signed) elevation diff between n and prev[n]
        self._ele_diff = {}
        visited = set()
        priority_queue = heapdict()

        # Disable lazy loading to prevent infinite chunks from being loaded
        self.graph_provider.lazy_loading_enabled = False

        self._prev[start] = None
        self._dist[start] = 0.
        self._ele_diff[start] = 0.
        priority_queue[start] = self._dist[start]
        while len(priority_queue) > 0:
            curr_node, curr_dist = priority_queue.popitem()
            visited.add(curr_node)
            neighbors = list(self.graph_provider.get_neighbors(curr_node))
            for n in neighbors:
                if n in visited:
                    continue
                alt_path_dist = self._dist[curr_node] + self._distance(curr_node, n)
                curr_ele_diff = self._elevation(n) - self._elevation(curr_node)
                # Standard Dijkstra criterion for updating path
                if alt_path_dist < self._dist[n]:
                    self._ele_diff[n] = curr_ele_diff
                    self._dist[n] = alt_path_dist
                    self._prev[n] = curr_node
                    priority_queue[n] = self._dist[n]

        # Reenable lazy loading
        # This does nothing if the graph provider does not support lazy loading
        self.graph_provider.lazy_loading_enabled = True

        result = {
            'prev': self._prev,
            'dist': self._dist,
            'ele_diff': self._ele_diff
        }

        return result

    def _reconstruct_result(self, node, end_is_source):
        """After concluding a targeted search, reconstruct the result.

        That is, follow backpointers and accumulate the elevation gain
        accordingly.

        Args:
            node: The target node of the search.
            end_is_source: See arg of same name on the `search` method.

        Returns:
            A SearchResult describing the path found.
        """
        path = [node]
        if end_is_source:
            # 'node' is the start point and so does not contribute to ele_gain.
            cum_ele_diff = 0
        else:
            # The ele diff between 'node' (end point) and next node
            # on the path toward the source
            cum_ele_diff = max([0., self._ele_diff[node]])

        # Follow backpointers to reconstruct path and compute statistics
        successor = node
        curr_node = self._prev[node]
        while curr_node is not None:
            path.append(curr_node)
            if end_is_source:
                # ele_diff's were computed moving forward toward 'node', so we
                # must be careful to get the right contribution here
                cum_ele_diff += max([0., -self._ele_diff[successor]])
            else:
                cum_ele_diff += max([0., self._ele_diff[curr_node]])
            curr_node = self._prev[curr_node]
            successor = curr_node
        if not end_is_source:
            path.reverse() # 'node' should be at final index in the list
        path_len = self._dist[node]
        return SearchResult(path, path_len, cum_ele_diff)

    def search(self, start, end, max_path_len=math.inf, end_is_source=False):
        """Perform a targeted search from 'start' to 'end'.

        If max_path_len is infinity, this will be a straightforward
        shortest-path search, but otherwise the algorithm will search for an
        elevation-minimizing path by heuristically weighing edges according
        to how much elevation gain achieved by following them.

        Args:
            start: The start node of the path of interest.
            end: The end node of the path of interest.
            max_path_len: The maximum allowable length of a path.
            end_is_source: If True, indicates that although we want a path
                from 'start' to 'end', we want to conduct the search by
                beginning at 'end' and finding a path to 'start', then
                reversing the path and computing elevation gain as if we
                moved from 'start' to 'end'.

        Returns:
            A SearchResult describing the path we found, or a default
            SearchResult in the event no path was found.
        """
        # Should we attempt to minimize elevation?
        minimize_ele = max_path_len < math.inf

        # A mapping from nodes to backpointers for reconstructing paths
        self._prev = {}
        # The distance of the current minimum-distance path to a node
        self._dist = {}
        # The weight of the current minimum-weight path to a node
        weight = defaultdict(lambda: math.inf)
        # Map a node 'n' to the (signed) elevation diff between n and prev[n]
        self._ele_diff = {}
        visited = set()
        priority_queue = heapdict()

        source = start if not end_is_source else end

        self._prev[source] = None
        self._dist[source] = 0.
        weight[source] = 0.
        self._ele_diff[source] = 0.
        priority_queue[source] = weight[source]
        while len(priority_queue) > 0:
            curr_node, curr_weight = priority_queue.popitem()

            # When a node is visited, its values in  dist, prev, weight,
            # and ele_diff will never be updated again
            visited.add(curr_node)
            if curr_node == start and end_is_source:
                return self._reconstruct_result(start, end_is_source=end_is_source)
            elif curr_node == end and not end_is_source:
                return self._reconstruct_result(end, end_is_source=end_is_source)

            # Explore neighbors to see if we have a new best path to them
            neighbors = list(self.graph_provider.get_neighbors(curr_node))
            for i, n in enumerate(neighbors):
                if n in visited:
                    continue

                alt_path_dist = self._dist[curr_node] + self._distance(curr_node, n)
                ele_n = self._elevation(n)
                curr_ele_diff = ele_n - self._elevation(curr_node)
                if minimize_ele:
                    # Heuristically weight the edges with positive ele gain
                    heuristic_weight = max([0., curr_ele_diff])
                    alt_path_weight = curr_weight + heuristic_weight
                else:
                    alt_path_weight = alt_path_dist

                # Outer 'if' trivially satisfied when max is math.inf
                if alt_path_dist <= max_path_len:
                    if alt_path_weight < weight[n]:
                        self._ele_diff[n] = curr_ele_diff
                        self._dist[n] = alt_path_dist
                        weight[n] = alt_path_weight
                        self._prev[n] = curr_node
                        priority_queue[n] = weight[n]

        return SearchResult()
