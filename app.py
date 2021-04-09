from flask import Flask, render_template
import sys

# Initialize flask server
app = Flask(__name__, static_folder="frontend", template_folder="frontend")

# Serve frontend on root directory
@app.route("/")
def serve_frontend():
    return render_template('index.htm')

print('DONE!')

# Set debug mode to false if user specifies --prod flag
dev_mode = len(sys.argv) < 2 or sys.argv[1] != '--prod'

# Start server
app.debug=dev_mode
app.run(host='0.0.0.0')
