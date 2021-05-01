import osmnx
import math
from backend.search_algs.a_star import AStar
from backend.search_algs.dijkstra import Dijkstra
from backend.search_algs.midpoint_miracle import MidpointMiracle
from backend.graph_providers.loading_graph_provider import LoadingGraphProvider
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider
from backend.timeout import timeout

# This is a temporary implementation to get a full feedback loop
# @timeout(40)
def get_path(ori, dest, dist, ele, grph):
    
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
    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end, use_elevation=False)

    max_path_len = shortest_res['path_len']*int(dist)/100
    if ele == 'minimal':
        res = astar.search(graph_provider.start, graph_provider.end, max_path_len, use_elevation=True)
    elif ele == 'maximal':
        maximal = MidpointMiracle(graph_provider)
        res = maximal.search(graph_provider.start, graph_provider.end, max_path_len)
    else:
        res = {'path': shortest_res['path'], 'path_len': -1, 'ele_gain': -1}

    stats = [round(float(shortest_res['path_len'])), round(float(shortest_res['ele_gain'])), round(float(res['path_len'])), round(float(res['ele_gain']))]
    route = res['path']
    shortest_route = shortest_res['path']

    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    shortest_route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, shortest_route)]
    return route_coords, shortest_route_coords, stats
