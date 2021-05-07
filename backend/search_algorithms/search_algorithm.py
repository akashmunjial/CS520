from abc import ABC, abstractmethod


class SearchAlgorithm(ABC):
    @abstractmethod
    def __init__(self, graph_provider):
        pass

    @abstractmethod
    def search(self, start, end, **kwargs):
        pass
