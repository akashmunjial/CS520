class NodeIdWrapper(object):
    def __init__(self, node_map, node_id):
        self.node_map = node_map
        self.node_id = node_id

    def get_data(self):
        return self.node_map[self.node_id]

    def __lt__(self, other):
        self_heuristic_dist = self.node_map[self.node_id].heuristic_dist
        other_heuristic_dist = other.node_map[other.node_id].heuristic_dist
        return self_heuristic_dist < other_heuristic_dist

class NodeIdWrapperFactory(object):
    def __init__(self, node_map):
        self.node_map = node_map

    def make_wrapper(self, node_id):
        return NodeIdWrapper(self.node_map, node_id)