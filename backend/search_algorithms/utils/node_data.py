class NodeData(object):
    """Class to represent the node objects used in the search.

    Attributes:
        id: The id of the current node.
        parent: The id of the parent node.
        heuristic_dist: The heuristic value related to this node.
        actual_dist: The actual distance from the start node to the current node.
        elevation_gain: The cumulative elevation gain from the start node to the current node.
    """

    def __init__(self, id, parent=None, heuristic_dist=0, actual_dist=0, elevation_gain=0):
        super().__init__()
        self.id = id
        self.parent = parent
        self.heuristic_dist = heuristic_dist
        self.actual_dist = actual_dist
        self.elevation_gain = elevation_gain
