from abc import ABC, abstractmethod

class GraphProvider(ABC):
    @abstractmethod
    def get_neighbors(node):
        pass

    @abstractmethod
    def get_edge_distance(self, node1, node2):
        pass

    @abtractmethod
    def get_coords(self, node):
        pass
