import osmnx
from backend.aStarSearch import AStar
from backend.dijkstra import Dijkstra
from backend.loading_graph_provider import LoadingGraphProvider
from backend.bounded_graph_provider import BoundedGraphProvider
from backend.dijkstra import Dijkstra

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
        search_algo = AStar(graph_provider, ele, int(dist) * 1000000)
    route = search_algo.search(graph_provider.start, graph_provider.end)
    stats = [1000, 100, 1500, 500]
    
    # convert nodes to coordinates and return
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    return route_coords, stats