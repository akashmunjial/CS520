from abc import ABC, abstractmethod


class SearchAlgorithm(ABC):
    """Abstract class that all search algorithms must subclass.

    This is the Strategy pattern 'interface' that each of the search algorithm
    strategies must implement, allowing PathFinder to have a 'has-a' relationship
    to SearchAlgorithm instead of to concrete search algorithms.
    """

    @abstractmethod
    def __init__(self, graph_provider):
        pass

    @abstractmethod
    def search(self, start, end, **kwargs):
        """The function to execute the search from some start to some end node.

        Args:
            start: The start of the search, the source.
            end: The termination point of the search, the target.
            **kwargs: Additional parameters that can be set such as the max_path_len etc.
        """
        pass
