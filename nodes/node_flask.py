from flask import Flask, make_response, jsonify, request
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
    return make_response({"result": 'Running'}, 200)

@app.route('/process', methods=["PUT"])
def process_data():
    """Command Node to process data"""
    data = request.json
    
    if "data" not in data:
        return make_response({"error": "Missing Data"}, 400)
    node.master_addr = request.remote_addr
    t = threading.Thread(target=node.work, args=[data])
    t.start()
    return make_response({"result": "ok"}, 201)

@app.route('/update', methods=["PUT"])
def update_local_data():
    """Update the local data"""
    print("success!", flush=True)



