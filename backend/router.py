import osmnx
from backend.aStarSearch import AStar
from backend.graph_provider import GraphProvider
from backend.bounded_graph_provider import BoundedGraphProvider
from backend.dijkstra import Dijkstra

# This is a temporary implementation to get a full feedback loop
def get_route(ori, dest, dist, tran, ele):
    
    # translate geodata for osmnx '(lat, lng)' -> (lat, lng)
    try:
        start_coords = tuple(float(x) for x in ori[1:-1].split(', '))
        end_coords = tuple(float(x) for x in dest[1:-1].split(', '))
    except ValueError:
        print('User did not select origin and/or destiation')
        return []

    # get nearest nodes to origin and destination

    if False: # Change to True to use lazy loading (GraphProvider)
        graph_provider = GraphProvider()
        start = graph_provider.find_node_near(start_coords)
        end = graph_provider.find_node_near(end_coords)

        shortest = Dijkstra(graph_provider)
        _, length = shortest.search(start, end)
        astar = AStar(graph_provider, ele, dist*length/100)
        route = astar.search(start, end)
        route_coords = [(node['y'], node['x']) for node in map(graph_provider.get_coords, route)]
    else:
        bounded_graph_provider = BoundedGraphProvider(start_coords, end_coords)
        start = bounded_graph_provider.find_node_near(start_coords)
        end = bounded_graph_provider.find_node_near(end_coords)

        shortest = Dijkstra(bounded_graph_provider)
        _, length = shortest.search(start, end)
        astar = AStar(bounded_graph_provider, ele, dist*length/100)
        route = astar.search(start, end)
        route_coords = [(node['y'], node['x']) for node in map(bounded_graph_provider.get_coords, route)]
    
    # convert nodes to coordinates
    return route_coords