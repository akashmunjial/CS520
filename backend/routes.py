from flask import Blueprint, request, jsonify
import osmnx
import json

from backend.path_request import PathRequest
from backend.path_finder import PathFinder
from backend.search_algorithms.a_star import AStar
from backend.search_algorithms.dijkstra import Dijkstra
from backend.search_algorithms.midpoint_miracle import MidpointMiracle
from backend.graph_providers.loading_graph_provider import LoadingGraphProvider
from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider

routes = Blueprint('routes', __name__, template_folder='frontend')

@routes.route('/api', methods = ['POST'])
def route():
    """Get a route for the requested parameters.

    Args:
        origin: Stringified coordinates of the starting point.
        destination: Stringified coordinates of the ending point.
        distance: Stringified percent of the shortest route.
        elevation: String 'maximal', 'minimal' or 'shortest' for mode.
        graph: String 'bounded' or 'loading' for graph provider.

    Returns:
        A jsonified object containing the shortest route, new route, and stats.
    """

    # Get request data
    origin = request.form['origin']
    destination = request.form['destination']
    distance_percent = request.form['distance']
    ele_setting = request.form['elevation']
    graph_setting = request.form['graph']

    # Create a new path request
    path_request = PathRequest(origin, destination, distance_percent, ele_setting, graph_setting)

    # Instantiate algorithm objects
    shortest_path_cls = AStar
    max_ele_cls = MidpointMiracle
    min_ele_cls = AStar

    # Choose the graph provider
    if(graph_setting == 'bounded'):
        graph_provider_cls = BoundedGraphProvider
    else:
        graph_provider_cls = LoadingGraphProvider

    # Get recomended route
    finder = PathFinder(
            shortest_path_cls,
            max_ele_cls,
            min_ele_cls,
            graph_provider_cls)
    results = finder.find_path(path_request)
    if results == None:
        return jsonify(error="timeout")
    else:
        return jsonify(results)


@routes.route('/search', methods = ['POST'])
def search():
    """Get a route for the requested parameters.

    Args:
        place: String of the desired location.

    Returns:
        A jsonified object containing the coordinates of the place.

    Raises:
        Exception: Place not found.
    """

    # Get request data
    place = request.form['place']

    # Geocode place to coordinates
    try:
        coords = osmnx.geocoder.geocode(place)
    except Exception:
        coords = []

    # Return coordinates
    return jsonify(coords=coords)
