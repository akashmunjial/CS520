from flask import Blueprint, request
from backend.router import get_route

dummy_route = Blueprint('dummy_route', __name__, template_folder='templates')

@dummy_route.route('/api', methods = ['POST'])
def route():

    # Get request data
    origin = request.form['origin']
    destination = request.form['destination']
    distance = int(request.form['distance'])
    transport = request.form['transport']
    elevation = request.form['elevation']

    # Get recomended route
    route = get_route(origin, destination, distance, transport, elevation)
    return route
    #return origin + '<br>' + destination + '<br>' + distance + '<br>' + transport + '<br>' + elevation