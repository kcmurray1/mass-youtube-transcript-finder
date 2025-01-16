from flask import make_response, Blueprint, request, current_app
import threading
from nodes.node import Node
internal_bp = Blueprint("internal", __name__, url_prefix="/internal")


@internal_bp.route('/')
def home():
    """Check status of node"""
    node = current_app.config["NODE"]
    node.is_master = True
    return make_response({"result": node.is_master}, 200)

@internal_bp.route('/process', methods=["PUT"])
def process_data(node):
    """Command Node to process data"""
    data = request.json
    
    if "author" not in data or "phrase" not in data:
        return make_response({"error": "Missing Data"}, 400)
    
    node.master_addr = request.remote_addr
    t = threading.Thread(target=node.work, args=[data])
    t.start()
    return make_response({"result": "ok"}, 201)

@internal_bp.route('/update', methods=["PUT", "POST"])
def update_local_data(node):
    """Update the local data"""
    node.update_local_data(request.get_data(as_text=True))
    return make_response({"Result": "Updated"}, 201)