import osmnx
from backend.aStarSearch import AStar

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    point_a = osmnx.geocoder.geocode(ori)
    point_b = osmnx.geocoder.geocode(dest)
    n = max(point_a[0], point_b[0])
    s = min(point_a[0], point_b[0])
    e = max(point_a[1], point_b[1])
    w = min(point_a[1], point_b[1])
    # Note that this method may not work near the prime meridian
    graph = osmnx.graph.graph_from_bbox(n, s, e, w)
    start = osmnx.distance.get_nearest_node(graph, point_a)
    end = osmnx.distance.get_nearest_node(graph, point_b)

    astar = AStar(graph)
    route = astar.search(start, end)
    return '<br>'.join(str(node) for node in route)