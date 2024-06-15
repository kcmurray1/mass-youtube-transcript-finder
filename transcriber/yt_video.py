import time
class YtVideo:
    def __init__(self, video_info=None, video_url=None, video_author=None, video_title=None):
        # parse videoInfo: <title> by <author> <views> views Streamed <days> day ago <hours> hours, <minutes> minutes
        # HAPPY NEW YEAR! Let's wait for 2024 to arrive together~! by Nerissa Ravencroft Ch. hololive-EN 72,223 views Streamed 1 day ago 3 hours, 8 minutes
        # Search for " by " from the right to handle cases where the video title contains " by "
        if video_info:
            split_point = video_info.rfind(" by ")
        # <url> 
        self.title = video_info[:split_point] if not video_title else video_title
        self.author = video_info[split_point:] if not video_author else video_author
        self.url = video_url

    def get_author(self):
        return self.author
    
    def get_title(self):
        return self.title
    
    def get_url(self):
        return self.url

    def print(self):
        print(f"Title: {self.title}, Author: {self.author}, Url: {self.url}")
        
if __name__ == "__main__":
    info = "HAPPY NEW YEAR! Let's wait for 2024 to arrive by together~! by <Nerissa Ravencroft Ch. hololive-EN> <72,223> views Streamed <1 day ago 3 hours, 8 minutes>"
    start = time.perf_counter()
    test = YtVideo(info)
    test.print()
    end = time.perf_counter()
    print(f"Elapsed time {end - start:.6f} seoncds")

    



