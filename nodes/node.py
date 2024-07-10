import requests
from transcriber.transcript import TranscriptProcessor
from requests import exceptions

class Node:
    def __init__(self):
        self.is_master = False
        self.master_addr = None
        self.transcriber = TranscriptProcessor()

    def _get_data(self):
        """Get necessary data to distribute work
        Returns:
            A dictionary containing pertinent data
        """
        user_author_name = input("Channel name: ")
        user_phrase = input("Enter a phrase: ")
        url = None
        if not url:
            url = input("Enter a url: ")
        
        num_workers = 4

        videos = self.transcriber.find_videos(yt_url=url)
        print(f"Found a {len(videos)} total!")
        return {"author": user_author_name, "phrase": user_phrase, "videos": videos, "workers": num_workers}
    
    def non_distributed_work(self):
        self.is_master = True
        self.work(self._get_data())

    def distribute_work(self, worker_addresses):
        """Send work to nodes across a network
        Args:
            worker_addresses: a comma separated string of addresses of machines
            to distribute work to
        """
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
        """Perform work based on specifications and report to main node
        
        Args:
            data: A dict containing necessary details to perform work
        """

        # unpack data
        author, phrase, videos, num_threads = data.values()
        self.transcriber.channel_search(videos, num_workers=num_threads, author=author, phrase=phrase)

        # Report results to master node
        if not self.is_master:
            self.send_results({"author" : self.transcriber.current_author})
    
    def send_results(self, data):
        """send results from work to the main node

        Args:
            data: a dict containing metadata necessary for recipient to validate request
        """
        try:
            requests.post(f"http://{self.master_addr}:5000/update", json=data, files={"file": open(f"nodes/matches_{self.transcriber.current_author}.txt", 'rb')})
        except exceptions.ConnectionError:
            pass

    def update_local_data(self, text):
        """Write received data into local files
        
        Args:
            text: A large string representing text sent from a worker node
        """

        # Convert non-support encodings into supported ascii encodings
        text = text.encode('ascii', 'ignore')
        text = text.decode()

        with open(self.transcriber.result_file, 'a') as results:
            for line in text.split('\r\n'):
                results.write(line + '\n')

def balance(a, n):
    """evenly split items n-ways
    Args:
        a: A list of items to be split
        n: An int representing the number of splits to make
    Returns:
        A 2d list of where with n rows
    
    NOTE: If n is larger than the number of items in a, then
    this function will fill the first n rows, leaving the remaining ones empty

    Ex: 
    a = [1,2,3]
    n = 5
    balance(a,n) = [[1],[2],[3],[],[]]
    """
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

# Used to test balance()
if __name__ == "__main__":
    arr = [0,1,3]
    balance(arr, 5)