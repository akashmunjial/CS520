import osmnx
import math

from backend.graph_providers.graph_provider import GraphProvider
from backend.keys import api_key


class BoundedGraphProvider(GraphProvider):

    def __init__(self, start, end):
        # Get the bounding box of start/end points
        n = max(start[0], end[0])
        s = min(start[0], end[0])
        e = max(start[1], end[1])
        w = min(start[1], end[1])
        # Compute a reasonable margin to load around the bounding box
        longer_diff = max([abs(e - w), abs(n - s)])
        # Load the map inside the bounding box coordinates into a networkx MultiDiGraph
        self.graph = osmnx.graph.graph_from_bbox(n + longer_diff, s - longer_diff, e + longer_diff, w - longer_diff, simplify=False, network_type='walk')
        # Add elevation data into each node
        osmnx.elevation.add_node_elevations(self.graph, api_key=api_key)
        # Find the ids of the nodes in the graph closest to the start and end coordinates
        self.start = self._find_node_near(start)
        self.end = self._find_node_near(end)

    def _find_node_near(self, node):
        return osmnx.distance.get_nearest_node(self.graph, node, method='euclidean')

    def get_all_nodes(self):
        return self.graph.nodes

    def get_neighbors(self, node):
        return self.graph.neighbors(node)

    # Compute Euclidian distance between two nodes
    def get_distance_estimate(self, n1, n2):
        p1 = self.get_coords(n1)
        p2 = self.get_coords(n2)
        # d = sqrt((x - x')^2 + (y - y')^2 + (z - z')^2)
        return math.sqrt(
            (p1['x'] - p2['x']) ** 2 +
            (p1['y'] - p2['y']) ** 2 +
            (p1['z'] - p2['z']) ** 2
        )

    # Compute actual distance between two adjacent nodes
    def get_edge_distance(self, n1, n2):
        return self.graph.get_edge_data(n1, n2)[0]['length']

    # Get x, y, and z coordinates from a node id
    def get_coords(self, node):
        node_data = self.graph.nodes[node]
        return {
            'x': node_data['x'],
            'y': node_data['y'],
            'z': node_data['elevation']
        }
