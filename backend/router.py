import osmnx
from backend.aStarSearch import AStar
from backend.keys import api_key

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    
    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        point_a = tuple(float(x) for x in ori[1:-1].split(', '))
        point_b = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        print('User did not select origin and/or destiation')
        return []
    n = max(point_a[0], point_b[0])
    s = min(point_a[0], point_b[0])
    e = max(point_a[1], point_b[1])
    w = min(point_a[1], point_b[1])

    # get nearest road nodes to origin and destination
    try:
        # note: bbox needs an elegant solution for extending beyond the origin and destination
        # ideally this would be the lazy loading implementation, but the below code is servicable
        astar_graph = osmnx.graph.graph_from_bbox(n + abs(e - w), s - abs(e - w), e + abs(n - s), w - abs(e - w), simplify=False, network_type=tran)
    except ValueError:
        print('No nodes in bbox for network_type tran')
        return []
    start = osmnx.distance.get_nearest_node(astar_graph, point_a, method='euclidean')
    print('Start: ' + str(start))
    end = osmnx.distance.get_nearest_node(astar_graph, point_b, method='euclidean')
    print('End: ' + str(end))

    # add node elevations and run search algorithm
    osmnx.elevation.add_node_elevations(astar_graph, api_key=api_key)
    astar = AStar(astar_graph)
    route = astar.search(start, end)

    # convert nodes to coordinates
    route_coords = [(astar_graph.nodes[node]['y'], astar_graph.nodes[node]['x']) for node in route]
    return route_coords