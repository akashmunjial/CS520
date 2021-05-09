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
    """Graph provider implementation that lazily loads sections of the world map.

    Attributes:
        start: the id of the node closest to the origin
        end: the id of the node closest to the destination
        lazy_loading_enabled: controls whether additional chunks should be automatically loaded
    """

    def __init__(self, origin_coords, destination_coords):
        initial_chunks = self._compute_initial_area(origin_coords, destination_coords)
        self._load_chunk(initial_chunks['x'], initial_chunks['y'], initial_chunks['w'], initial_chunks['h'])
        self.start = osmnx.distance.get_nearest_node(cache['graph'], origin_coords, method='euclidean')
        self.end = osmnx.distance.get_nearest_node(cache['graph'], destination_coords, method='euclidean')
        self.lazy_loading_enabled = True

    def get_all_nodes(self):
        return cache['graph'].nodes
    
    def get_neighbors(self, node):
        """Lazily load necessary chunks before returning neighbors of a node

        If the passed node has neighbors which are outside the currently loaded portion
        of the map, this function will load the chunks they're in.

        Args:
            node: the id of the node to get the neighbors of

        Returns:
            The neighbors of the passed node.

        """
        neighbors = list(cache['graph'].neighbors(node))
        if self.lazy_loading_enabled:
            # If any of the node's neighbors fall outside the loaded chunks...
            # ...then load the chunk they belong to first
            for neighbor in neighbors:
                coords = cache['graph'].nodes[neighbor]
                cx = math.floor(coords['x'] / CHUNK_SIZE) * CHUNK_SIZE
                cy = math.floor(coords['y'] / CHUNK_SIZE) * CHUNK_SIZE
                if not self._is_chunk_loaded(cx, cy):
                    self._load_chunk(cx, cy)
        return neighbors

    def get_distance_estimate(self, n1, n2):
        """Estimate the distance between any two nodes, no edge necessary.

        This is useful as a heuristic. Using simple trigonometry, it 
        calculates the distance as the crow flies.

        Args:
            n1: The first node (its integer id).
            n1: The second node (its integer id).

        Returns:
            The estimated distance between the nodes expressed as a number.
        """
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
        """Download the map associated with the chunk at (x, y) and merge it into cache['graph']

        Args:
            x: The longitude of the chunk to load
            y: The latitude of the chunk to load
            w: The width (in chunks) to load
            h: The height (in chunks) to load
        """
        # Don't do anything if the chunks are already loaded
        if self._is_chunk_loaded(x, y, w, h):
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
                self._set_chunk_loaded(x1 + CHUNK_SIZE * i, y1 + CHUNK_SIZE * j)

    # Helper methods for checking whether a chunk is loaded and marking it as loaded

    def _is_chunk_loaded(self, x, y, w = 1, h = 1):
        """Check whether a given area is loaded

        Args:
            x: The longitude of the chunk to check
            y: The latitude of the chunk to check
            w: The width (in chunks) to check
            h: The height (in chunks) to check

        Returns:
            True if all the chunks in the specified area are loaded
        """
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)
        for i in range(w):
            for j in range(h):
                if not cache['loaded_chunks'][cx + i][cy + j]:
                    return False
        return True

    def _set_chunk_loaded(self, x, y):
        """Marks the chunk at (x, y) as loaded"""
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)
        cache['loaded_chunks'][cx][cy] = True

    def _compute_initial_area(self, start, end):
        """Computes the initial bounding box to load"""
        n = max(start[0], end[0])
        s = min(start[0], end[0])
        e = max(start[1], end[1])
        w = min(start[1], end[1])
        longer_diff = max(abs(e - w), abs(n - s))
        chunk_n = math.ceil((n + longer_diff) / CHUNK_SIZE)
        chunk_s = math.floor((s - longer_diff) / CHUNK_SIZE)
        chunk_e = math.ceil((e + longer_diff) / CHUNK_SIZE)
        chunk_w = math.floor((w - longer_diff) / CHUNK_SIZE)
        return {
            'x': chunk_w * CHUNK_SIZE,
            'y': chunk_s * CHUNK_SIZE,
            'w': chunk_e - chunk_w,
            'h': chunk_n - chunk_s
        }