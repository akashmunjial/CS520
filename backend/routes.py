"""Using Flask, receives and serves the requests made from the front end.
"""
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
    try:
        path_request = PathRequest(origin, destination, distance_percent, ele_setting, graph_setting)
    except ValueError:
        return jsonify(error="badcoords")

    # Get graph provider
    if(path_request.graph_setting == 'bounded'):
        graph_provider_cls = BoundedGraphProvider
    else:
        graph_provider_cls = LoadingGraphProvider
    graph_provider = graph_provider_cls(path_request.origin, path_request.destination)

    # Get shortest path algorithm
    shortest_path_algo = AStar(graph_provider)

    # Get elevation-based search algorithm
    if path_request.ele_setting == 'minimal':
        ele_search_algo = AStar(graph_provider)
    elif path_request.ele_setting == 'maximal':
        ele_search_algo = MidpointMiracle(graph_provider)
    else:
        ele_search_algo = None

    # Find path and handle timeout if necessary
    finder = PathFinder(shortest_path_algo, ele_search_algo, graph_provider)
    results = finder.find_path(path_request)
    if results == None:
        return jsonify(error="timeout")
    else:
        return jsonify(results)


@routes.route('/search', methods = ['POST'])
def search():
    """Given an address or place name, attempt to find coordinates.

    We use this especially to re-center the front-end map display at
    the coordinates so that the user need not manually scroll across
    long distances.

    Returns:
        A jsonified object containing the coordinates of the place if OSMNX
        succeeded in finding them, or else an empty list.
    """
    place = request.form['place']

    try:
        coords = osmnx.geocoder.geocode(place)
    except Exception:
        # Most likely because of incorrectly-typed input: allow
        # front end to handle the empty list
        coords = []

    return jsonify(coords=coords)
