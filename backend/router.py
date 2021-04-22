import osmnx
from backend.aStarSearch import AStar
from backend.keys import api_key

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    
    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    point_a = tuple(float(x) for x in ori[1:-1].split(', '))
    point_b = tuple(float(x) for x in dest[1:-1].split(', '))
    n = max(point_a[0], point_b[0])
    s = min(point_a[0], point_b[0])
    e = max(point_a[1], point_b[1])
    w = min(point_a[1], point_b[1])

    # get nearest road nodes to origin and destination
    road_graph = osmnx.graph.graph_from_bbox(n, s, e, w, simplify=False, network_type='drive')
    start = osmnx.distance.get_nearest_node(road_graph, point_a)
    end = osmnx.distance.get_nearest_node(road_graph, point_b)

    # run search algorithm on unsimplified graph of type tran
    astar_graph = osmnx.graph.graph_from_bbox(n, s, e, w, simplify=False, network_type=tran)
    osmnx.elevation.add_node_elevations(astar_graph, api_key=api_key)
    astar = AStar(astar_graph)
    route = astar.search(start, end)

    # convert nodes to coordinates
    route_coords = [(astar_graph.nodes[node]['y'], astar_graph.nodes[node]['x']) for node in route]
    return route_coords