import osmnx
from backend.aStarSearch import AStar
from backend.dijkstra import Dijkstra
from backend.loading_graph_provider import LoadingGraphProvider
from backend.bounded_graph_provider import BoundedGraphProvider

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
#def get_route(ori, dest, ele):
    
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

    #route = astar.search(start, end)
    shortest_path, shortest_path_len = dijkstra.search(start, end)
    print(f"Opt goal is: {ele}")
    print(f"Shortest len was: {shortest_path_len}")
    ele_path, ele_path_len = dijkstra.search(
            start, end, use_elevation=True,
            max_path_len=1.5*shortest_path_len,
            opt_goal=ele)
    print(f"Ele len was: {ele_path_len}")

    route = ele_path
    #route = shortest_path
    route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]

    # convert nodes to coordinates
    return route_coords
