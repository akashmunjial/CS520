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

    # Get recomended route
    route = get_route(origin, destination, distance, elevation)
    return jsonify(route=route)

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