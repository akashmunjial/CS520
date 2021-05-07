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

    # Get request data
    origin = request.form['origin']
    destination = request.form['destination']
    distance_percent = request.form['distance']
    ele_setting = request.form['elevation']
    graph_setting = request.form['graph']

    path_request = PathRequest(origin, destination, distance_percent, ele_setting, graph_setting)

    shortest_path_cls = AStar
    max_ele_cls = MidpointMiracle
    min_ele_cls = AStar
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

    # Get request data
    place = request.form['place']

    # Geocode place to coordinates
    try:
        coords = osmnx.geocoder.geocode(place)
    except Exception:
        coords = []

    # Return coordinates
    return jsonify(coords=coords)
