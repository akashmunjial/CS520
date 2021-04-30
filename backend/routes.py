from flask import Blueprint, request, jsonify
import osmnx
from backend.get_path import get_path

routes = Blueprint('routes', __name__, template_folder='frontend')

@routes.route('/api', methods = ['POST'])
def route():

    # Get request data
    origin = request.form['origin']
    destination = request.form['destination']
    distance = request.form['distance']
    elevation = request.form['elevation']
    graph = request.form['graph']

    # Get recomended route
    results = get_path(origin, destination, distance, elevation, graph)
    if results == None:
        return jsonify(error="timeout")
    else:
        return jsonify(route=results[0], stats=results[1])

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