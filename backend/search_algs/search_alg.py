from abc import ABC, abstractmethod

class SearchAlg(ABC):
    @abstractmethod
    def __init__(self, graph_provider):
        pass

    @abstractmethod
    def search(self, start, end, max_path_len, **kwargs):
        pass