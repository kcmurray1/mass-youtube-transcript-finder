from flask import Flask
from .internal_routes import internal_bp
from node.node import Node

def create_node():
    app = Flask(__name__)
    
    # node = Node(num_threads=num_threads, is_master=is_master, worker_list=worker_addr_list)
    # app.config["NODE"] = node
    app.register_blueprint(internal_bp)

    return app