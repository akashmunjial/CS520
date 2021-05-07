class NodeData(object):
    def __init__(self, id, parent = None, heuristic_dist = 0, actual_dist = 0, elevation_gain = 0):
        super().__init__()
        self.id = id
        self.parent = parent
        self.heuristic_dist = heuristic_dist
        self.actual_dist = actual_dist
        self.elevation_gain = elevation_gain
