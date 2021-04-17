import osmnx
from backend.aStarSearch import AStar
from backend.keys import api_key

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    
    # translate geodata for osmnx
    point_a = osmnx.geocoder.geocode(ori)
    point_b = osmnx.geocoder.geocode(dest)
    n = max(point_a[0], point_b[0])
    s = min(point_a[0], point_b[0])
    e = max(point_a[1], point_b[1])
    w = min(point_a[1], point_b[1])
    
    # translate data for astar
    graph = osmnx.graph.graph_from_bbox(n, s, e, w)
    osmnx.elevation.add_node_elevations(graph, api_key=api_key)
    start = osmnx.distance.get_nearest_node(graph, point_a)
    # access elevation with graph.nodes[<node id>]['elevation']
    end = osmnx.distance.get_nearest_node(graph, point_b)
    ### get nearest node kinda sucks... simplify=False? ###

    # run search algorithm
    astar = AStar(graph)
    route = astar.search(start, end)

    # convert nodes to coordinates
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]
    return route_coords