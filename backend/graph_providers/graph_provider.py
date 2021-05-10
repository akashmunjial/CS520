from abc import ABC, abstractmethod


class GraphProvider(ABC):
    """Abstract class that all graph providers must subclass.

    This is the Strategy pattern 'interface' that each of the graph provider
    strategies must implement, allowing PathFinder to have a 'has-a' relationship
    to GraphProvider instead of to concrete graph provider classes.
    """

    @abstractmethod
    def get_neighbors(self, node):
        """Get all immediate neighbors to a specified node.

        Args:
            node: The node of interest (its integer id).

        Returns:
            A list of neighboring node ids.
        """
        pass

    @abstractmethod
    def get_edge_distance(self, node1, node2):
        """Get the distance between two specified nodes.

        If two nodes have multiple connecting edges, this
        method should default to the shortest one availible.

        Args:
            node1: The first node (its integer id).
            node2: The second node (its integer id).

        Returns:
            The distance between the nodes expressed as a number.
        """
        pass

    @abstractmethod
    def get_coords(self, node):
        """Get the latitude and longitude of a node.

        This method is necessary to translate nodes to coordinates
        for the frontend to ultimately paint on the user interface.
        The frontend leaflet.js module does not use recognize the
        same node ids as osmnx.

        Args:
            node: The node of interest (its integer id).

        Returns:
            The distance between the nodes expressed as a number.
        """
        pass

    @abstractmethod
    def get_all_nodes(self):
        """Get all nodes in the existing graph.

        Returns:
            A list of every node contained in the graph.
        """
        pass
