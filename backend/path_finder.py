"""Orchestrates other modules to serve requests for paths.



"""
from backend.timeout import timeout
from backend.path_request import PathRequest
from backend.search_algorithms.search_algorithm import SearchAlgorithm
from backend.graph_providers.graph_provider import GraphProvider


class PathFinder:
    """
    """
    def __init__(self, shortest_path_algo, ele_search_algo, graph_provider):
        self.shortest_path_algo = shortest_path_algo
        self.ele_search_algo = ele_search_algo
        self.graph_provider = graph_provider

    @property
    def shortest_path_algo(self):
        return self._shortest_path_algo

    @shortest_path_algo.setter
    def shortest_path_algo(self, search_algo):
        if not isinstance(search_algo, SearchAlgorithm):
            raise ValueError(f"Shortest path search algorithm must be a subclass of SearchAlgorithm")
        self._shortest_path_algo = search_algo

    @property
    def ele_search_algo(self):
        return self._ele_search_algo

    @ele_search_algo.setter
    def ele_search_algo(self, search_algo):
        if search_algo is not None and not isinstance(search_algo, SearchAlgorithm):
            raise ValueError(f"Elevation-based search algorithm may be None or a subclass of SearchAlgorithm")
        self._ele_search_algo = search_algo

    @property
    def graph_provider(self):
        return self._graph_provider

    @graph_provider.setter
    def graph_provider(self, graph_provider):
        if not isinstance(graph_provider, GraphProvider):
            raise ValueError(f"Graph provider must be a subclass of GraphProvider")
        self._graph_provider = graph_provider

    @timeout(80)
    def find_path(self, request):
        assert isinstance(request, PathRequest)
        start = self.graph_provider.start
        end = self.graph_provider.end

        # Compute shortest path
        shortest_res = self.shortest_path_algo.search(start, end)

        # Compute path with desired quality
        res = shortest_res
        if self.ele_search_algo is not None:
            max_path_len = shortest_res.path_len * request.distance_percent / 100
            alt_res = self.ele_search_algo.search(start, end, max_path_len)
            if request.ele_setting == 'minimal' and alt_res.ele_gain < res.ele_gain:
                res = alt_res
            elif request.ele_setting == 'maximal' and alt_res.ele_gain > res.ele_gain:
                res = alt_res

        return self._make_result_json(shortest_res, res)

    # Calculates the information that is displayed by the frontend
    def _make_result_json(self, shortest_res, res):
        route = res.path
        shortest_route = shortest_res.path

        # Convert list of node ids to (lat, lng) coordinates
        route_coords = [(node['y'], node['x']) for node in map(self.graph_provider.get_coords, route)]
        shortest_route_coords = [(node['y'], node['x']) for node in map(self.graph_provider.get_coords, shortest_route)]

        # Return coordinate sequences and route statistics
        return {
            'route': route_coords,
            'shortRoute': shortest_route_coords,
            'stats': {
                'shortestPath': {
                    'pathLength': round(shortest_res.path_len),
                    'elevationGain': round(shortest_res.ele_gain)
                },
                'resultPath': {
                    'pathLength': round(res.path_len),
                    'elevationGain': round(res.ele_gain)
                }
            }
        }
