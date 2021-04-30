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



#     #astar = AStar(graph_provider)
#     dijkstra = Dijkstra(graph_provider)
#     max_search = MidpointMiracle(graph_provider)

#     #route = astar.search(start, end)
#     shortest_res = dijkstra.search(start, end)
#     shortest_path = shortest_res['path']
#     shortest_path_len = shortest_res['path_len']
#     shortest_path_gain = shortest_res['ele_gain']

#     if ele != 'shortest':
#         best_res = shortest_res # Default
#         if ele == 'maximal':
#             result = max_search.search(
#                     start, end,
#                     max_path_len=(dist / 100)*shortest_path_len)
#             best_ele_gain = shortest_path_gain
#             if result['ele_gain'] > best_ele_gain:
#                 best_ele_gain = result['ele_gain']
#                 best_res = result
#         else:
#             # Forward
#             forward_res = dijkstra.search(
#                     start, end, use_elevation=True,
#                     max_path_len=(dist / 100)*shortest_path_len,
#                     backward=False)
#             # Backward
#             backward_res = dijkstra.search(
#                     end, start, use_elevation=True,
#                     max_path_len=(dist / 100)*shortest_path_len,
#                     backward=True)
#             best_ele_gain = shortest_path_gain
#             for result in [forward_res, backward_res]:
#                 if result['ele_gain'] < best_ele_gain:
#                     best_ele_gain = result['ele_gain']
#                     best_res = result

#         route = best_res['path']
#     else:
#         route = shortest_path

#     route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]

#     # convert nodes to coordinates
#     return route_coords
    # Choose graph type
    if(grph == 'bounded'):
        graph_provider = BoundedGraphProvider(start_coords, end_coords)
    else:
        graph_provider = LoadingGraphProvider(start_coords, end_coords)
    
    # Choose between Dijkstra and AStar based on form input
    # if(ele == 'shortest'):
    #     search_algo = Dijkstra(graph_provider)
    # else:
    #     search_algo = AStar(graph_provider, ele, int(dist) * 1000000)
    # route = search_algo.search(graph_provider.start, graph_provider.end)
    shortest = Dijkstra(graph_provider)
    path, length = shortest.search(graph_provider.start, graph_provider.end)
    search = AStar(graph_provider, ele, int(dist)*length/100)
    route = search.search(graph_provider.start, graph_provider.end)
    stats = [1000, 100, 1500, 500]
    
    # convert nodes to coordinates and return
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    return route_coords, stats
