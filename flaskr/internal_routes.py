from flask import make_response, Blueprint, request, current_app
import threading
from node.node import Node
from transcriber.screaper_threaded import ScraperThreaded
from transcriber.logger import DBLogger
from dotenv import load_dotenv
from mysql.connector import pooling
import os

internal_bp = Blueprint("internal", __name__, url_prefix="/internal")


@internal_bp.route('/')
def home():
    """Check status of node"""
    node : Node = current_app.config["NODE"]
    return make_response({"status": "online", "is_master" : node.is_master}, 201)

@internal_bp.route('/process', methods=["PUT"])
def process_data():
    """Command Node to process data"""
    data = request.json
    if "videos" not in data:
        return make_response({"error": "Missing Videos"}, 400)
    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])

  
    load_dotenv()
    dbconfig = {
        'database' : os.getenv('DEV_DB'),
            'user': os.getenv('USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'host' :'localhost'
    }
    conn_pool = pooling.MySQLConnectionPool(
        pool_size=10,
        pool_name="worker_pool",
        **dbconfig

    )
    db = DBLogger(conn_pool)
    t = threading.Thread(target=ScraperThreaded.get_transcripts, args=(data["videos"], "", db, default_transcript, 4))
    t.start()
    return make_response({"result": "ok"}, 201)

# used for when data is written to file locally
@internal_bp.route('/update', methods=["PUT", "POST"])
def update_local_data():
    """Update the local data"""
    node : Node = current_app.config["NODE"]
    node.update_local_data(request.get_data(as_text=True))
    return make_response({"Result": "Updated"}, 201)