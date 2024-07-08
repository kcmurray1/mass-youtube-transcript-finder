import collections


instance_attributes = ['channel', 'url', 'phrase', 'vids', 'match_count']

class InstanceConfig(collections.namedtuple('InstanceConfig', instance_attributes)):
    def __str__(self):
        return f'{self.channel}, {self.vids} Videos'
    
class TestResult():
    def __init__(self):
        self.num_errors = 0
        self.videos = None

class ValidData:
    VALID_CHANNEL_URL = "https://www.youtube.com/@Flarvain/videos"
    VALID_VIDEO_URL = "https://www.youtube.com/watch?v=ZsIEzKRW1BE"

test_transcriber_valid_data = [ 
InstanceConfig(channel="jdh", url="https://www.youtube.com/@jdh/videos", phrase="hello", match_count=10, vids=23),
# InstanceConfig(channel="git-amend", url="https://www.youtube.com/@git-amend/videos", phrase="hello", match_count=10 , vids=68),  
]

class InvalidData:
    INVALID_GOOGLE_URL = InstanceConfig(channel="google", url="https://www.google.com", phrase="Hello World", match_count=1, vids=0)
    INVALID_NO_TRANSCRIPT = InstanceConfig(channel="Nuclear Blast Records", url="https://www.youtube.com/watch?v=Ui_eoW3BXGI", phrase="Rock", match_count=1, vids=1)

