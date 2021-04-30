import osmnx
from backend.aStarSearch import AStar
from backend.dijkstra import Dijkstra
from backend.midpoint_miracle import MidpointMiracle
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
    shortest = AStar(graph_provider, 'shortest')
    shortest_res = shortest.search(graph_provider.start, graph_provider.end)

    limit = shortest_res['path_len']*int(dist)/100
    if ele == 'minimal':
        minimal = AStar(graph_provider, 'minimal', limit)
        res = minimal.search(graph_provider.start, graph_provider.end)
    elif ele == 'maximal':
        maximal = MidpointMiracle(graph_provider)
        res = maximal.search(graph_provider.start, graph_provider.end, max_path_len = limit)
    else:
        res = {'path': shortest_res['path'], 'path_len': -1, 'ele_gain': -1}

    stats = [round(float(shortest_res['path_len'])), round(float(shortest_res['ele_gain'])), round(float(res['path_len'])), round(float(res['ele_gain']))]
    route = res['path']
    shortest_route = shortest_res['path']

    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    shortest_route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, shortest_route)]
    return route_coords, shortest_route_coords, stats
