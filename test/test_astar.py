from backend.search_algorithms.a_star import AStar
from backend.graph_providers.graph_provider import GraphProvider


def build_graph_provider():
    nodes = [1,2,3,4,5]

    neighbors = {}
    neighbors[1] = [2,3,5]
    neighbors[2] = [1,3,4]
    neighbors[3] = [1,2,5]
    neighbors[4] = [2,5]
    neighbors[5] = [1,4,3]

    edges = {}
    edges[(1,2)] = 5
    edges[(1,3)] = 8
    edges[(1,5)] = 5
    edges[(2,3)] = 4
    edges[(2,4)] = 9
    edges[(3,5)] = 8
    edges[(4,5)] = 10
    for n1, lst in neighbors.items():
        for n2 in lst:
            if (n1, n2) in edges and (n2, n1) not in edges:
                edges[(n2,n1)] = edges[(n1,n2)]

    node2ele = {}
    node2ele[1] = 8
    node2ele[2] = 5
    node2ele[3] = 6
    node2ele[4] = 3
    node2ele[5] = 0

    coords = {}
    coords[1] = [1,0]
    coords[2] = [0,0]
    coords[3] = [0,1]
    coords[4] = [0,-1]
    coords[5] = [-1,0]
    #Path 5-1-2 is the shortest with ele gain = 8
    #Path 5-4-2 has lowest ele gain of 5 but >150% of shortest path
    #Path 5-3-2 has lowest elegain with length length <= 150% of shortest path

    graph_provider = PlayProvider(nodes, neighbors, edges, node2ele, coords)
    return graph_provider

def test_shortest_path():
    graph_provider = build_graph_provider()
    astar = AStar(graph_provider)
    shortest_path = astar.search(5,2)

    assert shortest_path.path == [5,1,2]
    assert shortest_path.path_len == 10
    assert shortest_path.ele_gain == 8

def test_minimum_elevation_gain():
    graph_provider = build_graph_provider()
    astar = AStar(graph_provider)
    shortest_path = astar.search(5,2)

    assert shortest_path.path_len == 10
    assert shortest_path.ele_gain == 8

    min_elevation = astar.search(5,2,15)

    assert min_elevation.path == [5,3,2]
    assert min_elevation.path_len == 12
    assert min_elevation.ele_gain == 6

class PlayProvider(GraphProvider):

    def __init__(self, nodes: list, neighbors: dict, edges: dict, node2ele: dict, coords: dict):
        assert None not in [nodes, neighbors, edges, node2ele, coords], "Inputs may not be None"

        self.nodes = nodes
        self.neighbors = neighbors
        self.edges = edges
        self.node2ele = node2ele
        self.coords = coords

    def get_neighbors(self, node):
        return self.neighbors[node]

    def get_edge_distance(self, n1, n2):
        return self.edges.get((n1,n2))

    def get_coords(self, node):
        return {'z': self.node2ele[node], 'x': self.coords[node][0], 'y': self.coords[node][1]}

    def get_all_nodes(self):
        return self.nodes

