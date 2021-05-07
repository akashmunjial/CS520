import osmnx
import networkx as nx
from collections import defaultdict
import math

from backend.keys import api_key
from backend.graph_providers.graph_provider import GraphProvider

# Side length of chunk in degrees
CHUNK_SIZE = 0.01

# The keys to the loaded_chunks dict are given as integers in units of CHUNK_SIZE
# (e.g. if CHUNK_SIZE=0.01, then the bool describing whether chunk with...
# ...northeast corner (12deg, 12deg) would be stored in loaded_chunks[1200][1200])
cache = {
    'loaded_chunks': defaultdict(lambda: defaultdict(lambda: False)),
    'graph': nx.MultiDiGraph()
}

class LoadingGraphProvider(GraphProvider):
    def __init__(self, origin_coords, destination_coords):
        self.start = self._find_node_near(origin_coords)
        self.end = self._find_node_near(destination_coords)

    def _find_node_near(self, coords):
        # Load a 3x3 chunk square around the specified (lat, lng) coordinates
        x = coords[1]
        y = coords[0]
        chunk_x = math.floor(x / CHUNK_SIZE) * CHUNK_SIZE
        chunk_y = math.floor(y / CHUNK_SIZE) * CHUNK_SIZE
        self._load_chunk(chunk_x - CHUNK_SIZE, chunk_y - CHUNK_SIZE, 3, 3)
        # Once the chunks are loaded, then the nearest node can be calculated
        return osmnx.distance.get_nearest_node(cache['graph'], coords, method='euclidean')

    def get_all_nodes(self):
        return cache['graph'].nodes

    # Lazily loads chunks before returning neighbors of a node
    def get_neighbors(self, node):
        neighbors = list(cache['graph'].neighbors(node))
        # If any of the node's neighbors fall outside the loaded chunks...
        # ...then load the chunk they belong to first
        for neighbor in neighbors:
            coords = cache['graph'].nodes[neighbor]
            cx = math.floor(coords['x'] / CHUNK_SIZE) * CHUNK_SIZE
            cy = math.floor(coords['y'] / CHUNK_SIZE) * CHUNK_SIZE
            if not self.is_chunk_loaded(cx, cy):
                self._load_chunk(cx, cy)
        return neighbors

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
        return cache['graph'].get_edge_data(n1, n2)[0]['length']

    # Get x, y, and z coordinates from a node id
    def get_coords(self, node):
        node_data = cache['graph'].nodes[node]
        return {
            'x': node_data['x'],
            'y': node_data['y'],
            'z': node_data['elevation']
        }

    def _load_chunk(self, x, y, w = 1, h = 1):
        # Don't do anything if the chunks are already loaded
        if self.is_chunk_loaded(x, y, w, h):
            return
        # Get the northwest corner of the chunk
        x1 = math.floor(x / CHUNK_SIZE) * CHUNK_SIZE
        y1 = math.floor(y / CHUNK_SIZE) * CHUNK_SIZE
        # Get the southeast corner of the chunk
        x2 = x1 + CHUNK_SIZE * w
        y2 = y1 + CHUNK_SIZE * h
        compose = nx.algorithms.operators.binary.compose
        # Download the chunk as a graph, including edges that cross the chunk boundary
        subgraph = osmnx.graph.graph_from_bbox(y2, y1, x2, x1, simplify=False, truncate_by_edge=True)
        # Add elevation data to the loaded chunk
        osmnx.elevation.add_node_elevations(subgraph, api_key)
        # Merge the loaded chunk into the current graph
        cache['graph'] = compose(cache['graph'], subgraph)
        # Mark all the chunks as loaded
        for i in range(w):
            for j in range(h):
                self.set_chunk_loaded(x1 + CHUNK_SIZE * i, y1 + CHUNK_SIZE * j)

    # Helper methods for checking whether a chunk is loaded and marking it as loaded

    def is_chunk_loaded(self, x, y, w = 1, h = 1):
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)
        for i in range(w):
            for j in range(h):
                if not cache['loaded_chunks'][cx + i][cy + j]:
                    return False
        return True

    def set_chunk_loaded(self, x, y):
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)
        cache['loaded_chunks'][cx][cy] = True

