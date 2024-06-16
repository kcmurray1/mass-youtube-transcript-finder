from flask import Flask, make_response, jsonify, request, send_file, send_from_directory
from nodes.node import Node
import threading
node = Node()


app = Flask(__name__)

def run_flask(new_node):
    global node
    node = new_node
    app.run(host='0.0.0.0', debug=False)

@app.route('/')
def home():
    """Check status of node"""
    return send_file("error_log.txt")
    # return make_response({"result": 'Running'}, 200)

@app.route('/process', methods=["PUT"])
def process_data():
    """Command Node to process data"""
    data = request.json
    
    if "author" not in data or "phrase" not in data:
        return make_response({"error": "Missing Data"}, 400)
    

    node.master_addr = request.remote_addr
    t = threading.Thread(target=node.work, args=[data])
    t.start()
    return make_response({"result": "ok"}, 201)

@app.route('/update', methods=["PUT", "POST"])
def update_local_data():
    """Update the local data"""
    print(request.get_data(as_text=True))
    return make_response({"Result": "Updated"}, 201)


