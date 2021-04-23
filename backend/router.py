import osmnx
from backend.aStarSearch import AStar
from backend.graph_provider import GraphProvider

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    
    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        point_a = tuple(float(x) for x in ori[1:-1].split(', '))
        point_b = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        print('User did not select origin and/or destiation')
        return []

    # get nearest road nodes to origin and destination

    graph_provider = GraphProvider()
    start = graph_provider.find_node_near(point_a[1], point_a[0])
    end = graph_provider.find_node_near(point_b[1], point_b[0])
    osmnx.plot_graph(graph_provider.graph)

    astar = AStar(graph_provider)
    route = astar.search(start, end)
    osmnx.plot_graph(graph_provider.graph)

    # convert nodes to coordinates
    route_coords = [(node['x'], node['y']) for node in map(graph_provider.get_coords, route)]
    return route_coords