from nodes.node import Node
from nodes.node_flask import run_flask
from tests.test import start_tests
import sys
import argparse

p = argparse.ArgumentParser()
p.add_argument('--test', action='store_true')
options, args = p.parse_known_args()

def assign_work():
    """Determine whether to treat this instance as a master or worker node"""
    if options.test:
        test()
    else:
        node = Node()
        if len(sys.argv) > 1:
            node.distribute_work(sys.argv[1])
        
        run_flask(node)


def test():
    start_tests()
    # node = Node()
    # node.master_addr = '10.0.0.222'
    # node.transcriber.current_author = None
    # node.send_results({'author':'hello'})

if __name__ == "__main__":
    assign_work()