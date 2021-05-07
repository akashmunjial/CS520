import osmnx
import math
from backend.search_algs.search_result import SearchResult
from backend.search_algs.a_star import AStar
from backend.search_algs.dijkstra import Dijkstra
from backend.search_algs.midpoint_miracle import MidpointMiracle
from backend.graph_providers.loading_graph_provider import LoadingGraphProvider
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider
from backend.timeout import timeout

@timeout(80)
def get_path(ori, dest, dist, ele, grph):
    
    # Translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        start_coords = tuple(float(x) for x in ori[1:-1].split(', '))
        end_coords = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        return { 'error': 'badcoords' }

    # Choose graph type
    if(grph == 'bounded'):
        graph_provider = BoundedGraphProvider(start_coords, end_coords)
    else:
        graph_provider = LoadingGraphProvider(start_coords, end_coords)

    # Compute shortest path
    astar = AStar(graph_provider)
    shortest_res = astar.search(graph_provider.start, graph_provider.end, use_elevation=False)

    # Compute path with desired quality
    max_path_len = shortest_res.path_len * int(dist) / 100
    res = shortest_res
    alt_res = None
    if ele == 'minimal':
        alt_res = astar.search(graph_provider.start, graph_provider.end, max_path_len, use_elevation=True)
    elif ele == 'maximal':
        maximal = MidpointMiracle(graph_provider)
        alt_res = maximal.search(graph_provider.start, graph_provider.end, max_path_len)
    if alt_res is not None:
        if ele == 'maximal' and alt_res.ele_gain > res.ele_gain:
            res = alt_res
        elif ele == 'minimal' and alt_res.ele_gain < res.ele_gain:
            res = alt_res

    return make_result_json(graph_provider, shortest_res, res)

# Calculates the information that is displayed by the frontend
def make_result_json(graph_provider, shortest_res, res):
    route = res.path
    shortest_route = shortest_res.path

    # Convert list of node ids to (lat, lng) coordinates
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    shortest_route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, shortest_route)]

    # Return coordinate sequences and route statistics
    return {
        'route': route_coords,
        'shortRoute': shortest_route_coords,
        'stats': {
            'shortestPath': {
                'pathLength': round(shortest_res.path_len),
                'elevationGain': round(shortest_res.ele_gain)
            },
            'resultPath': {
                'pathLength': round(res.path_len),
                'elevationGain': round(res.ele_gain)
            }
        }
    }
