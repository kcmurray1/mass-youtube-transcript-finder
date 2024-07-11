from nodes.node import Node
from nodes.node_flask import run_flask
from tests.test import start_tests
import sys
import argparse



def assign_work():
    """Determine whether to treat this instance as a master or worker node"""
    
    p = argparse.ArgumentParser()

    # https://stackoverflow.com/questions/11154946/require-either-of-two-arguments-using-argparse
    group = p.add_mutually_exclusive_group()
    group.add_argument('--test', action='store_true', help="Determine whether to run system test suite")
    group.add_argument('-d', '--distr', type=str, help="Comma separated addresses to other machines")
    options, _ = p.parse_known_args()

    # Run Test Suite
    if options.test:
        test()
        return
    node = Node()
    # Act as main node and distribute work to other machines 
    if options.distr:
        node.distribute_work(options.distr)
        run_flask(node)
    # Act as main node and do not distribute work
    else:
        node.non_distributed_work()
   


def test():
    start_tests()
    # node = Node()
    # node.master_addr = '10.0.0.222'
    # node.transcriber.current_author = None
    # node.send_results({'author':'hello'})

if __name__ == "__main__":
    assign_work()