from flask import Blueprint, request

dummy_route = Blueprint('dummy_route', __name__, template_folder='templates')

@dummy_route.route('/api', methods = ['POST'])
def route():
    origin = request.form['origin']
    destination = request.form['destination']
    distance = request.form['distance']
    transport = request.form['transport']
    elevation = request.form['elevation']
    return origin + '<br>' + destination + '<br>' + distance + '<br>' + transport + '<br>' + elevation