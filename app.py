"""Basic setup of the server with Flask.
"""
from flask import Flask, render_template, request
import sys

from backend.routes import routes

# Initialize flask server
app = Flask(__name__, static_folder="frontend", template_folder="frontend")

# Serve frontend on root directory
@app.route('/')
def serve_frontend():
    return render_template('index.htm')

app.register_blueprint(routes)

# Set debug mode to false if user specifies --prod flag
dev_mode = len(sys.argv) < 2 or sys.argv[1] != '--prod'
app.debug=dev_mode

# Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0')
