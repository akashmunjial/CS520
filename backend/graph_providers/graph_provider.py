from abc import ABC, abstractmethod

class GraphProvider(ABC):
    @abstractmethod
    def get_neighbors(self, node):
        pass

    @abstractmethod
    def get_edge_distance(self, node1, node2):
        pass

    @abstractmethod
    def get_coords(self, node):
        pass

    @abstractmethod
    def get_all_nodes(self):
        pass
