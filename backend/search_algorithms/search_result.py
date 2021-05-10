class SearchResult(object):
    """Class representing a return object for a search query.

    Attributes:
        path: An array representing the path from a start node to the end node, empty if there is no path.
        path_len: The length of the path represented by path, 0 if path is empty.
        ele_gain: The cumulative elevation gain through the path, 0 if path is empty.
    """
    def __init__(self, path=[], path_len=0, ele_gain=0):
        self.path = path
        self.path_len = path_len
        self.ele_gain = ele_gain
