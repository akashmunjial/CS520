import heapq
import math

from backend.keys import api_key
from backend.search_algorithms.utils.node_data import NodeData
from backend.search_algorithms.utils.node_id_wrapper import NodeIdWrapper, NodeIdWrapperFactory
from backend.search_algorithms.search_result import SearchResult
from backend.search_algorithms.search_algorithm import SearchAlgorithm


class AStar(SearchAlgorithm):
    """Class to perform the complete A* search

    Attributes:
        graph_provider: The instance of the graph_provider used for fetching
            points and other information.
    """

    def __init__(self, graph_provider):
        self.graph_provider = graph_provider

    def _elevation_heuristic(self, node1, node2):
        """Calculate the elevation heuristic between the two given nodes.

        Args:
            node1: Node id of the source node.
            node2: Node id of the target node.

        Returns:
            A value representing the heuristic for the elevation model between node1 and node2
        """
        n1 = self.graph_provider.get_coords(node1)
        n2 = self.graph_provider.get_coords(node2)
        elevation_gain = max(0, (n2['z'] - n1['z'])**3)
        return elevation_gain

    def _elevation_gain(self, node1, node2):
        """Calculate the elevation gain between the two given nodes.

        Args:
            node1: Node id of the source node.
            node2: Node id of the target node.

        Returns:
            A value representing the elevation gain from node1 to node2.
        """
        n1 = self.graph_provider.get_coords(node1)
        n2 = self.graph_provider.get_coords(node2)
        return max(0, (n2['z'] - n1['z']))

    def _distance_heuristic(self, node1, node2):
        """Calculate the distance heuristic between the two given nodes.

        Args:
            node1: Node id of the source node.
            node2: Node id of the target node.

        Returns:
            A value representing the euclidean distance between node1 and node2.
        """
        n1 = self.graph_provider.get_coords(node1)
        n2 = self.graph_provider.get_coords(node2)
        return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)

    def _distance(self, node1, node2):
        """Lookup the distance between two nodes from the graph provider.

        Args:
            node1: node id of the source node
            node2: node id of the target node

        Returns:
            A value representing the length of the edge between node1 and node2
        """
        return self.graph_provider.get_edge_distance(node1, node2)

    def search(self, start, end, max_path_len=math.inf):
        """The function to execute the A* search from the given start to given end node

        Args:
            start: the start of the search, the source
            end: the termination point of the search, the target
            max_path_len: the upper limit for the length of the path to find, infinity to indicate finding the shortest path

        Returns:
            A SearchResult object containing the path, path length and elevation gain
        """
        use_elevation = max_path_len < math.inf
        visited_nodes = set()
        node_data_map = { start: NodeData(start) }
        wrap_node_id = NodeIdWrapperFactory(node_data_map).make_wrapper
        nodes_to_visit = [wrap_node_id(start)]

        while len(nodes_to_visit) > 0:
            curr = heapq.heappop(nodes_to_visit).get_data()
            visited_nodes.add(curr.id)

            if curr.id == end:
                return SearchResult(
                    path=self._make_path(curr, node_data_map),
                    path_len=curr.actual_dist,
                    ele_gain=curr.elevation_gain
                )

            neighbors = self.graph_provider.get_neighbors(curr.id)
            unvisited_neighbors = filter(lambda n: n not in visited_nodes, neighbors)
            for n in unvisited_neighbors:
                dist = curr.actual_dist + self._distance(curr.id, n)
                if dist <= max_path_len:
                    is_in_node_map = n in node_data_map
                    dist_heuristic = dist + self._distance_heuristic(n, end)
                    elevation_heuristic = curr.elevation_gain + self._elevation_heuristic(curr.id, n)
                    node_data_map[n] = NodeData(
                        id=n,
                        parent=curr.id,
                        heuristic_dist=elevation_heuristic if use_elevation else dist_heuristic,
                        actual_dist=dist,
                        elevation_gain=curr.elevation_gain + self._elevation_gain(curr.id, n)
                    )
                    if is_in_node_map:
                        heapq.heapify(nodes_to_visit)
                    else:
                        heapq.heappush(nodes_to_visit, wrap_node_id(n))

        return SearchResult()

    def _make_path(self, end_node, node_data_map):
        """Back-track the path from the end node to the start node.

        Args:
            end_node: the ending node to start back tracking the path
            node_data_map: Mapping of the node ids to their respective objects

        Returns:
            An array containing the node ids representing the path, where first node id is start and last is the end
        """
        path = []
        curr = end_node
        while curr.parent is not None:
            path.insert(0, curr.id)
            curr = node_data_map[curr.parent]
        path.insert(0, curr.id)
        return path
