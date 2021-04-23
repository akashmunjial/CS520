import osmnx
from backend.keys import api_key
import math

class BoundedGraphProvider():

    def __init__(self, start, end):
        n = max(start[0], end[0])
        s = min(start[0], end[0])
        e = max(start[1], end[1])
        w = min(start[1], end[1])
        self.graph = osmnx.graph.graph_from_bbox(n + abs(e - w), s - abs(e - w), e + abs(n - s), w - abs(e - w), simplify=False)
        osmnx.elevation.add_node_elevations(self.graph, api_key=api_key)

    def find_node_near(self, node):
        return osmnx.distance.get_nearest_node(self.graph, node, method='euclidean')

    def get_neighbors(self, node):
        return self.graph.neighbors(node)

    def get_distance_estimate(self, n1, n2):
        p1 = self.get_coords(n1)
        p2 = self.get_coords(n2)
        return math.sqrt(
            (p1['x'] - p2['x']) ** 2 +
            (p1['y'] - p2['y']) ** 2 +
            (p1['z'] - p2['z']) ** 2
        )

    def get_edge_distance(self, n1, n2):
        return self.graph.get_edge_data(n1, n2)[0]['length']

    def get_coords(self, node):
        node_data = self.graph.nodes[node]
        return {
            'x': node_data['x'],
            'y': node_data['y'],
            'z': node_data['elevation']
        }