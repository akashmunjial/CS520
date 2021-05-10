"""Some integration tests testing MidPoint miracle with real-world data.
"""
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider
from backend.search_algorithms.a_star import AStar
from backend.search_algorithms.midpoint_miracle import MidpointMiracle

def test_midpoint_miracle_real_world_1():
    # Expect: path found with maximum elevation gain within max_path_len
    start_coords = (42.387229, -72.526106)
    end_coords = (42.372044, -72.516836)
    distance_percent = 200

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    mm = MidpointMiracle(graph_provider)
    alt_res = mm.search(graph_provider.start, graph_provider.end, max_path_len)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= round(shortest_res.path_len, 3)
    assert alt_res.ele_gain > round(shortest_res.ele_gain, 3)


def test_midpoint_miracle_real_world_2():
    # Expect: path found with maximum elevation gain within max_path_len
    start_coords = (42.3506, -71.168575)
    end_coords = (42.354778, -71.162766)
    distance_percent = 200

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    mm = MidpointMiracle(graph_provider)
    alt_res = mm.search(graph_provider.start, graph_provider.end, max_path_len)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= round(shortest_res.path_len, 3)
    assert alt_res.ele_gain > round(shortest_res.ele_gain, 3)


def test_midpoint_miracle_real_world_3():
    # Expect: no path found with maximum elevation gain within max_path_len
    start_coords = (42.472358, -71.120054)
    end_coords = (42.470771, -71.117066)
    distance_percent = 300

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    mm = MidpointMiracle(graph_provider)
    alt_res = mm.search(graph_provider.start, graph_provider.end, max_path_len)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= round(shortest_res.path_len, 3)
    assert not alt_res.ele_gain > round(shortest_res.ele_gain, 3)


def test_midpoint_miracle_real_world_4():
    # Expect: no path found with maximum elevation gain within max_path_len
    start_coords = (42.47326, -71.106445)
    end_coords = (42.464531, -71.09504)
    distance_percent = 300

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    mm = MidpointMiracle(graph_provider)
    alt_res = mm.search(graph_provider.start, graph_provider.end, max_path_len)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= round(shortest_res.path_len, 3)
    assert not alt_res.ele_gain > round(shortest_res.ele_gain, 3)
