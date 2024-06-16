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
    res = requests.get("http://10.0.0.4:5000/", json=dict())

    # print(res.json())
    file_data = res.content.decode()

    if file_data:
        print(file_data)
    else:
        print("No data")

if __name__ == "__main__":
    assign_work()
    # test()