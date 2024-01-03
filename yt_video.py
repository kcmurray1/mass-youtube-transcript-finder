import re
class Yt_Video:
    def __init__(self, video_info=None, video_url=None):
        # parse videoInfo <title> <views> <post date>
        # HAPPY NEW YEAR! Let's wait for 2024 to arrive together~! by Nerissa Ravencroft Ch. hololive-EN 72,223 views Streamed 1 day ago 3 hours, 8 minutes
        # <url>
        self.title = video_info
        self.url = video_url
    
    def get_title(self):
        return self.title
    
    def get_url(self):
        return self.url

    def print(self):
        print(f"Title: {self.title}, Url: {self.url}")
        
if __name__ == "__main__":
    info = "<HAPPY NEW YEAR! Let's wait for 2024 to arrive together~!> by <Nerissa Ravencroft Ch. hololive-EN> <72,223> views Streamed <1 day ago 3 hours, 8 minutes>"
    Yt_Video(info)