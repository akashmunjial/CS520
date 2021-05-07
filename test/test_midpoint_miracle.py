from play_graph_provider import PlayProvider
from backend.search_algorithms.midpoint_miracle import MidpointMiracle


def build_downhill_best_graph_provider():
    """ For testing min elevation gain algorithm. The point is that
    chokepoints can cause problems for an algorithm which greedily
    tries to minimize elevation gain and can only "visit" a node exactly
    once.
    """
    nodes = [1,2,3,4]

    neighbors = {}
    neighbors[1] = [2,3,4]
    neighbors[2] = [1,4]
    neighbors[3] = [1,4]
    neighbors[4] = [2,3,1]

    edges = {}
    edges[(1,4)] = 10
    edges[(1,2)] = 10
    edges[(1,3)] = 10
    edges[(2,4)] = 1
    edges[(3,4)] = 1
    for n1, lst in neighbors.items():
        for n2 in lst:
            if (n1, n2) in edges and (n2, n1) not in edges:
                edges[(n2,n1)] = edges[(n1,n2)]

    node2ele = {}
    node2ele[1] = 20.
    node2ele[4] = 20.
    node2ele[3] = 39.
    node2ele[2] = 0.

    graph_provider = PlayProvider(nodes, neighbors, edges, node2ele)
    return graph_provider


def build_pruning_best_graph_provider():
    nodes = [1,2,3,4,5,6]

    neighbors = {}
    neighbors[1] = [2,3]
    neighbors[2] = [1,4,6]
    neighbors[3] = [1,5]
    neighbors[4] = [2,6]
    neighbors[5] = [3,6]
    neighbors[6] = [2,4,5]

    edges = {}
    edges[(1,2)] = 1
    edges[(1,3)] = 1
    edges[(3,5)] = 1
    edges[(2,4)] = 1
    edges[(2,6)] = 1
    edges[(4,6)] = 1
    edges[(5,6)] = 1
    for n1, lst in neighbors.items():
        for n2 in lst:
            if (n1, n2) in edges and (n2, n1) not in edges:
                edges[(n2,n1)] = edges[(n1,n2)]

    node2ele = {}
    node2ele[1] = 5.
    node2ele[6] = 5.
    node2ele[2] = 15.
    node2ele[4] = 14.
    node2ele[3] = 0.
    node2ele[5] = 13.

    graph_provider = PlayProvider(nodes, neighbors, edges, node2ele)
    return graph_provider


def test_goes_downhill():
    graph_provider = build_downhill_best_graph_provider()

    shortest_path_len = 10

    mm = MidpointMiracle(graph_provider)
    res = mm.search(1, 4, 1.1 * shortest_path_len)

    assert res.path == [1,2,4]
    assert res.ele_gain == 20.
    assert res.path_len == 11.


def test_pruning():
    graph_provider = build_pruning_best_graph_provider()
    mm = MidpointMiracle(graph_provider)

    shortest_path_len = 2

    # Point is, it should take a less good path
    res_no_prune = mm.search(1, 6, 1.5 * shortest_path_len, keep_n=2, prune_depth=0)
    assert res_no_prune.path == [1,2,6]
    assert res_no_prune.ele_gain == 10.
    assert res_no_prune.path_len == 2.

    res_prune = mm.search(1, 6, 1.5 * shortest_path_len, keep_n=2, prune_depth=1)
    assert res_prune.path == [1,3,5,6]
    assert res_prune.ele_gain == 13.
    assert res_prune.path_len == 3.

