import osmnx
from backend.aStarSearch import AStar
from backend.dijkstra import Dijkstra
from backend.loading_graph_provider import LoadingGraphProvider
from backend.bounded_graph_provider import BoundedGraphProvider
from backend.max_algo import MaxSearch

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):

    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        start_coords = tuple(float(x) for x in ori[1:-1].split(', '))
        end_coords = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        print('User did not select origin and/or destination')
        return []

    # get nearest nodes to origin and destination

    graph_provider = BoundedGraphProvider(start_coords, end_coords)
    # graph_provider = LoadingGraphProvider()
    start = graph_provider.find_node_near(start_coords)
    end = graph_provider.find_node_near(end_coords)

    #astar = AStar(graph_provider)
    dijkstra = Dijkstra(graph_provider)
    max_search = MaxSearch(graph_provider)

    #route = astar.search(start, end)
    shortest_res = dijkstra.search(start, end)
    shortest_path = shortest_res['path']
    shortest_path_len = shortest_res['path_len']
    shortest_path_gain = shortest_res['ele_gain']
    print(f"====SHORTEST PATH STATS====")
    print(f"Shortest path len was: {shortest_path_len}")
    print(f"Shortest path ele gain was: {shortest_path_gain}")
    print()

    if ele != 'shortest':
        best_res = shortest_res # Default
        if ele == 'maximal':
            result = max_search.search(
                    start, end,
                    max_path_len=(dist / 100)*shortest_path_len,
                    backward=False)
            best_ele_gain = shortest_path_gain
            if result['ele_gain'] > best_ele_gain:
                best_ele_gain = result['ele_gain']
                best_res = result
        else:
            # Forward
            forward_res = dijkstra.search(
                    start, end, use_elevation=True,
                    max_path_len=(dist / 100)*shortest_path_len,
                    backward=False)
            print(f"Forward ele gain was {forward_res['ele_gain']}")
            # Backward
            backward_res = dijkstra.search(
                    end, start, use_elevation=True,
                    max_path_len=(dist / 100)*shortest_path_len,
                    backward=True)
            print(f"Backward ele gain was {backward_res['ele_gain']}")
            best_ele_gain = shortest_path_gain
            for result in [forward_res, backward_res]:
                if result['ele_gain'] < best_ele_gain:
                    best_ele_gain = result['ele_gain']
                    best_res = result

        print(f"====BEST PATH STATS====")
        print(f"Best path len was: {best_res['path_len']}")
        print(f"Best path ele gain was: {best_res['ele_gain']}")
        print()
        route = best_res['path']
    else:
        route = shortest_path

    #route = shortest_path
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]

    # convert nodes to coordinates
    return route_coords
