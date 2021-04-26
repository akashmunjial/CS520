import osmnx
import networkx as nx
from collections import defaultdict
from backend.keys import api_key
import math
from backend.graph_provider import GraphProvider

CHUNK_SIZE = 0.01

class LoadingGraphProvider(GraphProvider):
    loaded_chunks = defaultdict(lambda: defaultdict(lambda: False))
    graph = nx.MultiDiGraph()

    def find_node_near(self, node):
        x = node[1]
        y = node[0]
        chunk_x = math.floor(x / CHUNK_SIZE) * CHUNK_SIZE
        chunk_y = math.floor(y / CHUNK_SIZE) * CHUNK_SIZE
        self.load_chunk(chunk_x - CHUNK_SIZE, chunk_y - CHUNK_SIZE, 3, 3)
        return osmnx.distance.get_nearest_node(self.graph, (y, x), method='euclidean')

    def get_neighbors(self, node):
        neighbors = list(self.graph.neighbors(node))
        for neighbor in neighbors:
            coords = self.graph.nodes[neighbor]
            cx = math.floor(coords['x'] / CHUNK_SIZE) * CHUNK_SIZE
            cy = math.floor(coords['y'] / CHUNK_SIZE) * CHUNK_SIZE
            if not self.is_chunk_loaded(cx, cy):
                self.load_chunk(cx, cy)
        return neighbors

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

    def load_chunk(self, x, y, w = 1, h = 1):
        x1 = math.floor(x / CHUNK_SIZE) * CHUNK_SIZE
        y1 = math.floor(y / CHUNK_SIZE) * CHUNK_SIZE
        x2 = x1 + CHUNK_SIZE * w
        y2 = y1 + CHUNK_SIZE * h
        compose = nx.algorithms.operators.binary.compose
        print(x2, x1, y2, y1)
        subgraph = osmnx.graph.graph_from_bbox(y2, y1, x2, x1, simplify=False, truncate_by_edge=True)
        osmnx.elevation.add_node_elevations(subgraph, api_key)
        self.graph = compose(self.graph, subgraph)
        for i in range(w):
            for j in range(h):
                self.set_chunk_loaded(x1 + CHUNK_SIZE * i, y1 + CHUNK_SIZE * j)

    def is_chunk_loaded(self, x, y):
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)
        return self.loaded_chunks[cx][cy]

    def set_chunk_loaded(self, x, y):
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)
        self.loaded_chunks[cx][cy] = True

