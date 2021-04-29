import osmnx
from backend.search_algs.a_star import AStar
from backend.search_algs.dijkstra import Dijkstra
from backend.graph_providers.loading_graph_provider import LoadingGraphProvider
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, ele, grph):
    
    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        start_coords = tuple(float(x) for x in ori[1:-1].split(', '))
        end_coords = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        print('User did not select origin and/or destination')
        return []

    # Choose graph type
    if(grph == 'bounded'):
        graph_provider = BoundedGraphProvider(start_coords, end_coords)
    else:
        graph_provider = LoadingGraphProvider(start_coords, end_coords)
    
    # Choose between Dijkstra and AStar based on form input
    if(ele == 'shortest'):
        search_algo = Dijkstra(graph_provider)
    else:
        search_algo = AStar(graph_provider, False, 99999)
    route = search_algo.search(graph_provider.start, graph_provider.end)
    
    # convert nodes to coordinates and return
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    return route_coords