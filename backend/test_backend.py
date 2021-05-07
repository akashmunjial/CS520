import pytest
from backend.search_algs.search_result import SearchResult
from backend.search_algs.a_star import AStar
from backend.search_algs.dijkstra import Dijkstra
from backend.search_algs.midpoint_miracle import MidpointMiracle
from backend.graph_providers.loading_graph_provider import LoadingGraphProvider
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider
from backend.timeout import timeout

class TestBackend:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")

    def test_aStarSearch_minimal(self):
        start_coords = (42.381357, -72.519357)
        end_coords = (42.398441, -72.515645)
        dist = 200
        ele = 'minimal'

        graph_provider = BoundedGraphProvider(start_coords, end_coords)

        astar = AStar(graph_provider)
        shortest_res = astar.search(graph_provider.start, graph_provider.end, use_elevation=False)

        max_path_len = shortest_res.path_len * int(dist) / 100
        alt_res = astar.search(graph_provider.start, graph_provider.end, max_path_len, use_elevation=True)

        assert alt_res.path_len > shortest_res.path_len
        assert alt_res.ele_gain < shortest_res.ele_gain