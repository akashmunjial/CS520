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

    Namely, we implement the single-source shortest paths version of Dijkstra
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
        prev = defaultdict(lambda: None)
        # The distance of the current minimum-distance path to a node
        dist = defaultdict(lambda: math.inf)
        # Map a node 'n' to the (signed) elevation diff between n and prev[n]
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
                alt_path_dist = dist[curr_node] + self._distance(curr_node, n)
                curr_ele_diff = self._elevation(n) - self._elevation(curr_node)
                # Standard Dijkstra criterion for updating path
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
        """Perform a targeted search from 'start' to 'end'.

        If max_path_len is infinity, this will be a straightforward
        shortest-path search, but otherwise the algorithm will search for an
        elevation-minimizing path by heuristically weighing edges according
        to how much elevation gain achieved by following them.

        Args:
            start: The start node of the path of interest.
            end: The end node of the path of interest.
            max_path_len: The maximum allowable length of a path.
            backward: If True, 'end' will be the source node, but the path we
                return will still begin with 'start' and end with 'end'. This is
                useful for investigating whether we can get a better elevation-
                minimizing path by starting from the end.

        Returns:
            A SearchResult describing the path we found, or a default
            SearchResult in the event no path was found.
        """
        # Should we attempt to minimize elevation?
        minimize_ele = max_path_len < math.inf

        # A mapping from nodes to backpointers for reconstructing paths
        prev = {}
        # The distance of the current minimum-distance path to a node
        dist = {}
        # The weight of the current minimum-weight path to a node
        weight = defaultdict(lambda: math.inf)
        # Map a node 'n' to the (signed) elevation diff between n and prev[n]
        ele_diff = {}
        visited = set()
        priority_queue = heapdict()

        ele_start = self._elevation(start)
        ele_end = self._elevation(end)

        prev[start] = None
        dist[start] = 0.
        weight[start] = 0.
        ele_diff[start] = 0.
        priority_queue[start] = weight[start]
        while len(priority_queue) > 0:
            curr_node, curr_weight = priority_queue.popitem()

            # When a node is visited, its values in  dist, prev, weight,
            # and ele_diff will never be updated again
            visited.add(curr_node)
            if curr_node == end:
                path = [end]
                predecessor = prev[end]
                cum_ele_diff = 0.
                # Reconstruct the path to 'end' using backpointers
                while predecessor is not None:
                    path.append(predecessor)
                    if backward:
                        cum_ele_diff += max([0., -ele_diff[predecessor]])
                    else:
                        cum_ele_diff += max([0., ele_diff[predecessor]])
                    predecessor = prev[predecessor]
                if not backward:
                    # Path currently starts with 'end': make begin with 'start'
                    path.reverse()
                path_len = dist[end]
                return SearchResult(path, path_len, cum_ele_diff)

            neighbors = list(self.graph_provider.get_neighbors(curr_node))

            for i, n in enumerate(neighbors):
                if n in visited:
                    continue

                alt_path_dist = dist[curr_node] + self._distance(curr_node, n)
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
                        ele_diff[n] = curr_ele_diff
                        dist[n] = alt_path_dist
                        weight[n] = alt_path_weight
                        prev[n] = curr_node
                        priority_queue[n] = weight[n]

        return SearchResult()
