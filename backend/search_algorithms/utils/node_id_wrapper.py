class NodeIdWrapper(object):
    """Wrapper class to wrap the node id associated with a node.

    Attributes:
        node_map: map of node ids to the corresponding NodeData objects
        node_id: the id corresponding to the current node
    """

    def __init__(self, node_map, node_id):
        self.node_map = node_map
        self.node_id = node_id

    def get_data(self):
        """Function to get the NodeData object corresponding to the current node id.

        Returns:
            NodeData object corresponding to the current node id
        """
        return self.node_map[self.node_id]

    def __lt__(self, other):
        """Operation override for the less than operation to compare two objects of the same type.

        Args:
            other: another object of the NodeIdWrapper time, with which current object has to be compared

        Returns:
            A boolean representing if the current node is less than the other node
        """
        self_heuristic_dist = self.node_map[self.node_id].heuristic_dist
        other_heuristic_dist = other.node_map[other.node_id].heuristic_dist
        return self_heuristic_dist < other_heuristic_dist

class NodeIdWrapperFactory(object):
    """Factory class to generate the wrappers.

    Attributes:
        node_map: map of node ids to the corresponding NodeData objects
    """

    def __init__(self, node_map):
        self.node_map = node_map

    def make_wrapper(self, node_id):
        """Function to create the wrapper for the node ids provided

        Args:
            node_id: the node id which is to be wrapped

        Returns:
            the NodeIdWrapper object corresponding to the given node_id
        """
        return NodeIdWrapper(self.node_map, node_id)