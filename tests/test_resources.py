import collections


instance_attributes = ['channel', 'url', 'phrase', 'vids', 'match_count']

class InstanceConfig(collections.namedtuple('InstanceConfig', instance_attributes)):
    def __str__(self):
        return f'{self.channel}, {self.vids} Videos'
    
class TestResult():
    def __init__(self):
        self.num_errors = 0
        self.videos = None

test_data = [ 
    InstanceConfig(channel="jdh", url="https://www.youtube.com/@jdh/videos", phrase="hello", match_count=10, vids=23),
    # InstanceConfig(channel="git-amend", url="https://www.youtube.com/@git-amend/videos", phrase="hello", vids=68),
    
]
