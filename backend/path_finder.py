"""Contains a class orchestrating several modules to do the work of finding paths.
"""
from backend.timeout import timeout
from backend.path_request import PathRequest
from backend.search_algorithms.search_algorithm import SearchAlgorithm
from backend.graph_providers.graph_provider import GraphProvider


class PathFinder:
    """Orchestrates several modules to perform EleNa's path finding.

    Attributes:
        shortest_path_algo: A SearchAlgorithm for finding the shortest path.
        ele_search_algo: None, if we only want shortest path, or else a
            SearchAlgorithm for performing an elevation-based search.
        graph_provider: A GraphProvider, which we need to access the endpoints
            and to be able to return paths as coordinate lists.
    """
    def __init__(self, shortest_path_algo, ele_search_algo, graph_provider):
        """Initializes a PathFinder, with input validation inside setters.
        """
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
        """Perform the work to obtain desired paths based on a request.

        Utilizes the graph provider and search algorithms to obtain the shortest
        path and, if an appropriate algorithm was provided, an elevation-based
        path. Wrapped in our timeout wrapper with a fixed timeout to avoid
        endlessly searching.

        Args:
            request: A PathRequest specifying nature of desired path.

        Returns:
            A dictionary containing the path(s) and relevant statistics to
            display on the front end.

        Raises:
            ValueError: If the input request is not of type PathRequest.
        """
        if not isinstance(request, PathRequest):
            raise ValueError(f"Request must be a PathRequest")

        start = self.graph_provider.start
        end = self.graph_provider.end

        # Compute shortest path
        shortest_res = self.shortest_path_algo.search(start, end)

        # Attempt to find alternate path with desired qualities
        alternate_res = None
        if self.ele_search_algo is not None:
            max_path_len = shortest_res.path_len * request.distance_percent / 100
            res = self.ele_search_algo.search(start, end, max_path_len)
            if request.ele_setting == 'minimal' and res.ele_gain < shortest_res.ele_gain:
                alternate_res = res
            elif request.ele_setting == 'maximal' and res.ele_gain > shortest_res.ele_gain:
                alternate_res = res
        # If we could not beat the shortest path (or did not try), default to that
        if alternate_res is None:
            alternate_res = shortest_res

        return self._make_result_json(shortest_res, alternate_res)

    def _make_result_json(self, shortest_res, alternate_res):
        """Translate the search results into a useable format for the front end.

        Args:
            shortest_res: The shortest-path SearchResult.
            alternate_res: The elevation-based SearchResult, or else the same
                as shortest_res if we could not beat it.

        Returns:
            A dict containing paths as sequences of (latitude, longitude)
            coordinates and statistics to display on the front end.
        """
        # Convert list of node ids to (lat, lng) coordinates
        get_coords = self.graph_provider.get_coords
        shortest_coords = [(node['y'], node['x']) for node in map(get_coords, shortest_res.path)]
        alternate_coords = [(node['y'], node['x']) for node in map(get_coords, alternate_res.path)]

        # Return coordinate sequences and route statistics
        return {
            'route': alternate_coords,
            'shortRoute': shortest_coords,
            'stats': {
                'resultPath': {
                    'pathLength': round(alternate_res.path_len),
                    'elevationGain': round(alternate_res.ele_gain)
                },
                'shortestPath': {
                    'pathLength': round(shortest_res.path_len),
                    'elevationGain': round(shortest_res.ele_gain)
                }
            }
        }
