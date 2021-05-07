import heapq
import math
import osmnx
from backend.keys import api_key 
from backend.search_algs.utils.node_data import NodeData
from backend.search_algs.utils.node_id_wrapper import NodeIdWrapper, NodeIdWrapperFactory
from backend.search_algs.search_result import SearchResult
from backend.search_algs.search_alg import SearchAlg

class AStar(SearchAlg):
    def __init__(self, graph):
        self.graph = graph
        
    def elevation_heuristic(self, node1, node2, find_maximal=False):
        n1 = self.graph.get_coords(node1)
        n2 = self.graph.get_coords(node2)
        elevation_gain = max(0, (n2['z'] - n1['z'])**3)
        return -elevation_gain if find_maximal else elevation_gain

    def elevation_gain(self, node1, node2):
        n1 = self.graph.get_coords(node1)
        n2 = self.graph.get_coords(node2)
        return max(0, (n2['z'] - n1['z']))

    def distance_heuristic(self, node1, node2):
        n1 = self.graph.get_coords(node1)
        n2 = self.graph.get_coords(node2)
        return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)

    def distance(self, node1, node2):
        return self.graph.get_edge_distance(node1, node2)

    def search(self, start, end, max_path_len=math.inf, use_elevation=False, find_maximal=False):
        visited_nodes = set()
        node_data_map = { start: NodeData(start) }
        wrap_node_id = NodeIdWrapperFactory(node_data_map).make_wrapper
        nodes_to_visit = [wrap_node_id(start)]

        while len(nodes_to_visit) > 0:
            curr = heapq.heappop(nodes_to_visit).get_data()
            visited_nodes.add(curr.id)

            if curr.id == end:
                return SearchResult(
                    path=self.make_path(curr, node_data_map),
                    path_len=curr.actual_dist,
                    ele_gain=curr.elevation_gain
                )

            neighbors = self.graph.get_neighbors(curr.id)
            unvisited_neighbors = filter(lambda n: n not in visited_nodes, neighbors)
            for n in unvisited_neighbors:
                dist = curr.actual_dist + self.distance(curr.id, n)
                if dist <= max_path_len:
                    is_in_node_map = n in node_data_map
                    
                    dist_heuristic = dist + self.distance_heuristic(n, end)
                    elevation_heuristic = curr.elevation_gain + self.elevation_heuristic(curr.id, n, find_maximal) 
                    node_data_map[n] = NodeData(
                        id=n,
                        parent=curr.id,
                        heuristic_dist=elevation_heuristic if use_elevation else dist_heuristic,
                        actual_dist=dist,
                        elevation_gain=curr.elevation_gain + self.elevation_gain(curr.id, n)
                    )
                    if is_in_node_map:
                        heapq.heapify(nodes_to_visit)
                    else:
                        heapq.heappush(nodes_to_visit, wrap_node_id(n))

        return SearchResult()

    def make_path(self, end_node, node_data_map):
        path = []
        curr = end_node
        while curr.parent is not None:
            path.insert(0, curr.id)
            curr = node_data_map[curr.parent]
        path.insert(0, curr.id)
        return path
