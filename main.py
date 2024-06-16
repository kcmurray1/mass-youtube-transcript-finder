from nodes.node import Node
from nodes.node_flask import run_flask
import requests
import sys


def assign_work():
    """Determine whether to treat this instance as a master or worker node"""

    node = Node()
    if len(sys.argv) > 1:
        node.distribute_work(sys.argv[1])
    
    run_flask(node)


def test():
    node = Node()
    node.master_addr = '10.0.0.222'
    node.transcriber.current_author = None
    node.send_results({'author':'hello'})

if __name__ == "__main__":
    # assign_work()
    test()