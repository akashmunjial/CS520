from play_graph_provider import PlayProvider
from backend.search_algorithms.dijkstra import Dijkstra


def build_generic_example():
    """ For testing min elevation gain algorithm. The point is that
    chokepoints can cause problems for an algorithm which greedily
    tries to minimize elevation gain and can only "visit" a node exactly
    once.
    """
    nodes = [1,2,3,4,5]

    neighbors = {}
    neighbors[1] = [2,3]
    neighbors[2] = [1,3,4,5]
    neighbors[3] = [1,2,4]
    neighbors[4] = [2,3,5]
    neighbors[5] = [2,4]

    edges = {}
    edges[(1,2)] = 3
    edges[(1,3)] = 1
    edges[(2,3)] = 7
    edges[(2,4)] = 5
    edges[(2,5)] = 1
    edges[(3,4)] = 2
    edges[(4,5)] = 7
    for n1, lst in neighbors.items():
        for n2 in lst:
            if (n1, n2) in edges and (n2, n1) not in edges:
                edges[(n2,n1)] = edges[(n1,n2)]

    node2ele = {}
    node2ele[1] = 7.
    node2ele[2] = 0.
    node2ele[3] = 5.
    node2ele[4] = 10.
    node2ele[5] = 2.

    graph_provider = PlayProvider(nodes, neighbors, edges, node2ele)
    return graph_provider


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

    # By performing the search "backwards" (setting end_is_source=True)
    # we will find a path that we could not have found otherwise
    expected_path = [1,3,5,6]
    result = dijkstra.search(1, 6, max_path_len=1.5*shortest_res.path_len, end_is_source=True)
    assert result.path == expected_path
    assert result.ele_gain == 5
    assert result.path_len == 115


def test_single_source():
    # Just a simple test of single-source shortest paths
    graph_provider = build_generic_example()
    dijkstra = Dijkstra(graph_provider)
    ss_res = dijkstra.single_source(3)

    prev = ss_res['prev']
    dist = ss_res['dist']
    ele_diff = ss_res['ele_diff']

    assert dist[1] == 1
    assert dist[2] == 4
    assert dist[3] == 0
    assert dist[4] == 2
    assert dist[5] == 5

    assert prev[1] == 3
    assert prev[2] == 1
    assert prev[3] == None
    assert prev[4] == 3
    assert prev[5] == 2

    assert ele_diff[1] == 2
    assert ele_diff[2] == -7
    assert ele_diff[3] == 0
    assert ele_diff[4] == 5
    assert ele_diff[5] == 2


def test_search_generic():
    # Just a simple test of shortest path search
    graph_provider = build_generic_example()
    dijkstra = Dijkstra(graph_provider)

    # Test that we find a fairly non-trivial path
    res = dijkstra.search(3, 5)
    assert res.path == [3,1,2,5]
    assert res.path_len == 5
    assert res.ele_gain == 4

    # Test of right values
    res = dijkstra.search(2, 3)
    assert res.path == [2,1,3]
    assert res.path_len == 4
    assert res.ele_gain == 7

    # Test of right values
    res = dijkstra.search(1, 4)
    assert res.path == [1,3,4]
    assert res.path_len == 3
    assert res.ele_gain == 5


def test_search_end_is_source_same():
    graph_provider = build_generic_example()
    dijkstra = Dijkstra(graph_provider)

    # Should behave exactly the same as forward dir
    res = dijkstra.search(3, 5, end_is_source=True)
    assert res.path == [3,1,2,5]
    assert res.path_len == 5
    assert res.ele_gain == 4
