import requests
from transcriber.transcript import TranscriptProcessor
from requests import exceptions

class Node:
    def __init__(self):
        self.is_master = False
        self.master_addr = None
        self.transcriber = TranscriptProcessor()

    def _get_data(self):
        user_author_name = input("Channel name: ")
        user_phrase = input("Enter a phrase: ")
        url = None
        if not url:
            url = input("Enter a url: ")
        
        num_workers = 5

        videos = self.transcriber.find_videos(yt_url=url)
        return {"author": user_author_name, "phrase": user_phrase, "videos": videos, "workers": num_workers}

    def distribute_work(self, worker_addresses):
        """Send work to nodes across a network"""
        self.is_master = True
        worker_addresses = worker_addresses.split(',')
        
        # Get data to distribute
        data = self._get_data()

        # split videos among number of workers including itself
        video_split = balance(data["videos"], len(worker_addresses) + 1)

        for worker_addr in worker_addresses:
            try:
                data["videos"] = video_split.pop()
                res = requests.put(f"http://{worker_addr}/process", json=data)
                print(res.json())
            except exceptions.ConnectionError:
                print(f"could not reach {worker_addr}")
        
        # Perform work on the remaining data
        for videos in video_split:
            data["videos"] = videos
            self.work(data)

    def work(self, data):
        """Receive dictionary of data"""
        # unpack data
        author, phrase, videos, num_threads = data.values()
        self.transcriber.channel_search(videos, num_workers=num_threads, author=author, phrase=phrase)

        # Report results to master node
        if not self.is_master:
            self.send_results({"author" : self.transcriber.current_author})
    
    def send_results(self, data):
        """send information to the master node
        """
        try:
            requests.post(f"http://{self.master_addr}:5000/update", json=data, files={"file": open(f"nodes/matches_{self.transcriber.current_author}.txt", 'rb')})
        except exceptions.ConnectionError:
            pass

    def update_local_data(self, text):

        text = text.encode('ascii', 'ignore')
        text = text.decode()

        with open(self.transcriber.result_file, 'a') as results:
            for line in text.split('\r\n'):
                results.write(line + '\n')

def balance(a, n):
    # split a among n buckets
    num_items = len(a)
    remainder = num_items % n

    split = num_items // n

    if not split:
        split = 1
    
    res = [list() for _ in range(n)]

    for i in range(n):
        cur_index = split * i
        end_index = cur_index + split
        
        # Ignore remainder if the split is set to 1
        if remainder and split !=1:
            end_index = cur_index + split + 1
            remainder -= 1
        res[i] += a[cur_index: end_index]
      

    return res


if __name__ == "__main__":
    arr = [0,1,3]
    balance(arr, 5)