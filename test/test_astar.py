import pytest
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider
from backend.search_algorithms.a_star import AStar

# Path found with minimal elevation gain within max_path_len
def test_a_star_minimal_real_world_1():
    start_coords = (42.433878, -71.083066)
    end_coords = (42.452167, -71.079741)
    distance_percent = 200

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    alt_res = astar.search(graph_provider.start, graph_provider.end, max_path_len)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= shortest_res.path_len
    assert alt_res.ele_gain < shortest_res.ele_gain

# Path found with minimal elevation gain within max_path_len
def test_a_star_minimal_real_world_2():
    start_coords = (42.420289, -71.216426)
    end_coords = (42.433862, -71.209152)
    distance_percent = 200

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    alt_res = astar.search(graph_provider.start, graph_provider.end, max_path_len)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= shortest_res.path_len
    assert alt_res.ele_gain < shortest_res.ele_gain

# No path found with minimal elevation gain within max_path_len
def test_a_star_minimal_real_world_3():
    start_coords = (42.381357, -72.519207)
    end_coords = (42.398504, -72.515581)
    distance_percent = 200

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    alt_res = astar.search(graph_provider.start, graph_provider.end, max_path_len)
    print(alt_res.ele_gain)
    print(shortest_res.ele_gain)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= shortest_res.path_len
    assert not alt_res.ele_gain < shortest_res.ele_gain

# No path found with minimal elevation gain within max_path_len
def test_a_star_minimal_real_world_4():
    start_coords = (42.448526, -71.130166)
    end_coords = (42.440878, -71.132441) 
    distance_percent = 200

    graph_provider = BoundedGraphProvider(start_coords, end_coords)

    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end)

    max_path_len = shortest_res.path_len * distance_percent / 100
    alt_res = astar.search(graph_provider.start, graph_provider.end, max_path_len)
    print(alt_res.ele_gain)
    print(shortest_res.ele_gain)

    assert alt_res.path_len < max_path_len
    assert alt_res.path_len >= shortest_res.path_len
    assert not alt_res.ele_gain < shortest_res.ele_gain