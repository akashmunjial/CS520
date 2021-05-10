import pytest

from backend.path_finder import PathFinder
from backend.path_request import PathRequest
from backend.search_algorithms.search_algorithm import SearchAlgorithm
from backend.search_algorithms.search_result import SearchResult
from backend.graph_providers.graph_provider import GraphProvider


class PlaySearch(SearchAlgorithm):
    """A mock search to test just the core functionality of PathFinder.
    """
    def __init__(self):
        pass

    def search(self, start, end, max_path_len=None):
        return SearchResult([1,4,2], 5, 10)


class PlayProvider(GraphProvider):
    """A mock provider to test just the core functionality of PathFinder.
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.nodes = [1,4,2]

    def get_neighbors(self):
        pass

    def get_all_nodes(self):
        pass

    def get_edge_distance(self):
        pass

    def get_coords(self, node):
        return {'x': 1, 'y': 2, 'z': 3}


def test_input_validation_init():
    search = PlaySearch()
    provider = PlayProvider(1, 2)

    # Should work
    finder = PathFinder(search, search, provider)
    finder = PathFinder(search, None, provider)

    # Cases that should throw an exception
    with pytest.raises(ValueError):
        finder = PathFinder(None, search, provider)
    with pytest.raises(ValueError):
        finder = PathFinder(search, 1, provider)
    with pytest.raises(ValueError):
        finder = PathFinder(search, search, None)


def test_find_path():
    search = PlaySearch()
    provider = PlayProvider(1, 2)

    # Make sure it handles the case of having no better path correctly
    finder = PathFinder(search, search, provider)
    request = PathRequest('(2, 2)', '(3, 3)', '150', 'maximal', 'bounded')
    output = finder.find_path(request)
    assert output['route'] == [(2,1), (2,1), (2,1)]
    assert output['shortRoute'] == [(2,1), (2,1), (2,1)]
    stats = output['stats']
    path_stats = stats['resultPath']
    shortest_stats = stats['shortestPath']
    assert path_stats['pathLength'] == 5
    assert path_stats['elevationGain'] == 10
    assert shortest_stats['pathLength'] == 5
    assert shortest_stats['elevationGain'] == 10

