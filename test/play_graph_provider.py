from backend.graph_providers.graph_provider import GraphProvider

class PlayProvider(GraphProvider):

    def __init__(self, nodes: list, neighbors: dict, edges: dict, node2ele: dict):
        assert None not in [nodes, neighbors, edges, node2ele], "Inputs may not be None"

        self.nodes = nodes
        self.neighbors = neighbors
        self.edges = edges
        self.node2ele = node2ele

    def get_neighbors(self, node):
        return self.neighbors[node]

    def get_edge_distance(self, n1, n2):
        return self.edges.get((n1,n2))

    def get_coords(self, node):
        return {'z': self.node2ele[node], 'x': None, 'y': None}

    def get_all_nodes(self):
        return self.nodes

