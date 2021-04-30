from flask import Blueprint, request, jsonify
import osmnx
from backend.router import get_route

dummy_route = Blueprint('dummy_route', __name__, template_folder='templates')

@dummy_route.route('/api', methods = ['POST'])
def route():

    # Get request data
    origin = request.form['origin']
    destination = request.form['destination']
    distance = request.form['distance']
    elevation = request.form['elevation']
    graph = request.form['graph']

    # Get recomended route
    route, short_route, stats = get_route(origin, destination, distance, elevation, graph)
    return jsonify(route=route, short_route=short_route, stats=stats)

@dummy_route.route('/search', methods = ['POST'])
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