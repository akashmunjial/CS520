from play_graph_provider import PlayProvider
from backend.search_algorithms.dijkstra import Dijkstra


def build_chokepoint_graph_provider():
    """ For testing min elevation gain algorithm. The point is that
    chokepoints can cause problems for an algorithm which greedily
    tries to minimize elevation gain and can only "visit" a node exactly
    once.
    """
    nodes = [1,2,3,4,5,6]

    neighbors = {}
    neighbors[1] = [2,3,4]
    neighbors[2] = [1,5]
    neighbors[3] = [1,5]
    neighbors[4] = [1,5]
    neighbors[5] = [2,3,4,6]
    neighbors[6] = [5]

    edges = {}
    edges[(1,2)] = 50
    edges[(2,5)] = 100
    edges[(1,3)] = 100
    edges[(3,5)] = 10
    edges[(1,4)] = 70
    edges[(4,5)] = 25
    edges[(5,6)] = 5
    for n1, lst in neighbors.items():
        for n2 in lst:
            if (n1, n2) in edges and (n2, n1) not in edges:
                edges[(n2,n1)] = edges[(n1,n2)]

    node2ele = {}
    node2ele[1] = 0.
    node2ele[6] = 0.

    node2ele[5] = 0.
    # Path through node 2 has smallest ele gain but exceeds 150% of shortest path
    node2ele[2] = 0.
    # Path through node 3 is within 150% of shortest path, plus has smaller ele gain than shortest path
    node2ele[3] = 5.
    # Node 4 taken by shortest path, hence ele gain is 10
    node2ele[4] = 10.

    graph_provider = PlayProvider(nodes, neighbors, edges, node2ele)
    return graph_provider


def test_min_ele_gets_stuck():
    graph_provider = build_chokepoint_graph_provider()
    dijkstra = Dijkstra(graph_provider)
    shortest_res = dijkstra.search(1, 6)

    assert shortest_res.path == [1,4,5,6]
    assert shortest_res.path_len == 100

    expected_path = []
    result = dijkstra.search(1, 6, max_path_len=1.5*shortest_res.path_len)
    # The point is that we will not find a path here, even though there
    # is a lower-elevation path within max_path_len
    assert result.path == expected_path


def test_min_ele_succeeds_backward():
    graph_provider = build_chokepoint_graph_provider()
    dijkstra = Dijkstra(graph_provider)
    shortest_res = dijkstra.search(1, 6)

    expected_path = [6,5,3,1]
    result = dijkstra.search(6, 1, max_path_len=1.5*shortest_res.path_len)
    assert result.path == expected_path
