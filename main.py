from nodes.node import Node
from nodes.node_flask import run_flask
import sys
import pyautogui
import os


def assign_work():
    """Determine whether to treat this instance as a master or worker node"""

    node = Node()
    if len(sys.argv) > 1:
        node.distribute_work(sys.argv[1])
    
    run_flask(node)


def test():
    node = Node()
    url = 'https://www.youtube.com/watch?v=MC7qoiJ5uPc'
    url_long_video = 'https://www.youtube.com/watch?v=SvwjrmKmggs'
    url_no_transcript = 'https://www.youtube.com/watch?v=IdVUOXkA7fk&list=RDwLj-vovaGRs&index=10'
    url_playlist = 'https://www.youtube.com/watch?v=7NxmTYDOPgA&list=PLDWPtsLTdtlDRtFlA61iRpY-ra_71vmAG'
    url_not_youtube = 'https://www.google.com/'
    url_homepage_27 = 'https://www.youtube.com/@jdh/videos'
    node.work(url='https://www.youtube.com/@EnnaAlouette/streams')


if __name__ == "__main__":
    assign_work()
    # test()