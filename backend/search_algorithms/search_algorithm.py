from abc import ABC, abstractmethod


class SearchAlgorithm(ABC):
    """Abstract class representing the necessary requirements for a class performing a search algorithm.
    """

    @abstractmethod
    def __init__(self, graph_provider):
        pass

    """The function to execute the search from some start to some end node

    Args:
        start: the start of the search, the source
        end: the termination point of the search, the target
        **kwargs: Additional parameters that can be set such as the max_path_len etc.
    """
    @abstractmethod
    def search(self, start, end, **kwargs):
        pass
