from flask import Flask
from .internal_routes import internal_bp
from nodes.node import Node

def create_node(num_threads=4, is_master=False, worker_addr_list=None):
    app = Flask(__name__)
    
    node = Node(num_threads=num_threads, is_master=is_master, worker_list=worker_addr_list)
    node.run()
    app.config["NODE"] = node
    app.register_blueprint(internal_bp)

    return app