import heapq
import math
import osmnx
from backend.keys import api_key 
from backend.search_algs.utils.node_data import NodeData
from backend.search_algs.utils.node_id_wrapper import NodeIdWrapper, NodeIdWrapperFactory

class AStar:
    def __init__(self, graph, is_maximal, limit):
        self.graph = graph
        self.is_maximal = is_maximal
        self.limit = limit
        
    def heuristic(self, node1, node2):
        n1 = self.graph.get_coords(node1)
        n2 = self.graph.get_coords(node2)
        # return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)
        elevation_gain = max(0, (n2['z'] - n1['z']) ** 3)
        return -elevation_gain if self.is_maximal else elevation_gain

    def distance(self, node1, node2):
        return self.graph.get_edge_distance(node1, node2)


    def search(self, start, end):
        visited_nodes = set()
        node_data_map = { start: NodeData(start) }
        wrap_node_id = NodeIdWrapperFactory(node_data_map).make_wrapper
        nodes_to_visit = [wrap_node_id(start)]

        while len(nodes_to_visit) > 0:
            curr = heapq.heappop(nodes_to_visit).get_data()
            visited_nodes.add(curr.id)

            if curr.id == end:
                return self.make_path(curr, node_data_map)

            neighbors = self.graph.get_neighbors(curr.id)
            unvisited_neighbors = filter(lambda n: n not in visited_nodes, neighbors)
            for n in unvisited_neighbors:
                dist = curr.actual_dist + self.distance(curr.id, n)
                if dist <= self.limit:
                    is_in_node_map = n in node_data_map
                    heuristic_dist = self.heuristic(curr.id, n)
                    node_data_map[n] = NodeData(
                        id=n,
                        parent=curr.id,
                        heuristic_dist=heuristic_dist,
                        actual_dist=dist,
                        elevation_gain=curr.elevation_gain + heuristic_dist
                    )

                    if is_in_node_map:
                        heapq.heapify(nodes_to_visit)
                    else:
                        heapq.heappush(nodes_to_visit, wrap_node_id(n))

        print("No path found")
        return []

    def make_path(self, end_node, node_data_map):
        path = []
        curr = end_node
        while curr.parent is not None:
            path.insert(0, curr.id)
            curr = node_data_map[curr.parent]
        path.insert(0, curr.id)
        print('Path Found: ', path)
        return path
