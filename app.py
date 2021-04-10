from flask import Flask, render_template, request
import sys

# Initialize flask server
app = Flask(__name__, static_folder="frontend", template_folder="frontend")

# Serve frontend on root directory
@app.route('/', methods = ['POST', 'GET'])
def serve_frontend():
    if request.method == 'GET':
        return render_template('index.htm')
    elif request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        distance = request.form['distance']
        transport = request.form['transport']
        elevation = request.form['elevation']
        return origin + '<br>' + destination + '<br>' + distance + '<br>' + transport + '<br>' + elevation


print('DONE!')

# Set debug mode to false if user specifies --prod flag
dev_mode = len(sys.argv) < 2 or sys.argv[1] != '--prod'

# Start server
app.debug=dev_mode
app.run(host='0.0.0.0')
