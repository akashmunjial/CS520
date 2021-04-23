import osmnx
from backend.aStarSearch import AStar
from backend.loading_graph_provider import LoadingGraphProvider
from backend.bounded_graph_provider import BoundedGraphProvider

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    
    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        start_coords = tuple(float(x) for x in ori[1:-1].split(', '))
        end_coords = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        print('User did not select origin and/or destiation')
        return []

    graph_provider = BoundedGraphProvider(start_coords, end_coords)
    # graph_provider = LoadingGraphProvider(start_coords, end_coords)
    astar = AStar(graph_provider)

    route = astar.search(graph_provider.start, end = graph_provider.end)
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    
    # convert nodes to coordinates
    return route_coords