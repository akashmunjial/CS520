from backend.timeout import timeout
from backend.search_algorithms.search_algorithm import SearchAlgorithm
from backend.graph_providers.graph_provider import GraphProvider

class PathFinder:
    def __init__(self,
            shortest_path_cls,
            max_ele_cls,
            min_ele_cls,
            graph_provider_cls):
        self.shortest_path_cls = shortest_path_cls
        self.max_ele_cls = max_ele_cls
        self.min_ele_cls = min_ele_cls
        self.graph_provider_cls = graph_provider_cls

    @property
    def shortest_path_cls(self):
        return self._shortest_path_cls

    @shortest_path_cls.setter
    def shortest_path_cls(self, cls):
        assert issubclass(cls, SearchAlgorithm)
        self._shortest_path_cls = cls

    @property
    def max_ele_cls(self):
        return self._max_ele_cls

    @max_ele_cls.setter
    def max_ele_cls(self, cls):
        assert issubclass(cls, SearchAlgorithm)
        self._max_ele_cls = cls

    @property
    def min_ele_cls(self):
        return self._min_ele_cls

    @min_ele_cls.setter
    def min_ele_cls(self, cls):
        assert issubclass(cls, SearchAlgorithm)
        self._min_ele_cls = cls

    @property
    def graph_provider_cls(self):
        return self._graph_provider_cls

    @graph_provider_cls.setter
    def graph_provider_cls(self, cls):
        assert issubclass(cls, GraphProvider)
        self._graph_provider_cls = cls

    @timeout(80)
    def find_path(self, request):
        graph_provider = self.graph_provider_cls(request.start_coords, request.end_coords)
        start = graph_provider.start
        end = graph_provider.end

        # Compute shortest path
        shortest_path_algo = self.shortest_path_cls(graph_provider)
        shortest_res = shortest_path_algo.search(start, end)

        # Compute path with desired quality
        res = shortest_res
        max_path_len = shortest_res.path_len * request.distance_percent / 100
        if request.ele_setting == 'minimal':
            min_ele_algo = self.min_ele_cls(graph_provider)
            alt_res = min_ele_algo.search(start, end, max_path_len)
            if alt_res.ele_gain < res.ele_gain:
                res = alt_res
        elif request.ele_setting == 'maximal':
            max_ele_algo = self.max_ele_cls(graph_provider)
            alt_res = max_ele_algo.search(start, end, max_path_len)
            if alt_res.ele_gain > res.ele_gain:
                res = alt_res

        return self.make_result_json(graph_provider, shortest_res, res)

    # Calculates the information that is displayed by the frontend
    def make_result_json(self, graph_provider, shortest_res, res):
        route = res.path
        shortest_route = shortest_res.path

        # Convert list of node ids to (lat, lng) coordinates
        route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
        shortest_route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, shortest_route)]

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
