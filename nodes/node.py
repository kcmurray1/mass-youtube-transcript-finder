import requests
from transcriber.transcript import TranscriptProcessor
from requests import exceptions

# FIXME: currently requests are hard coded to port 5000
DEBUG_DATA = ["jdh", "https://www.youtube.com/@jdh/videos", "hello"]

class Node:
    def __init__(self, num_threads=4, is_master=False, worker_list=None):
        self.is_master = is_master
        self.master_addr = None
        self.worker_addresses = worker_list
        self.transcriber = TranscriptProcessor()
        self.num_threads = num_threads
        if(is_master and worker_list):
            self.distribute_work(worker_addresses=self.worker_addresses)


    def _get_data(self):
        """Get necessary data to distribute work
        Returns:
            A dictionary containing the data: 
            {"author": user_author_name, "phrase": user_phrase, "videos": videos, "workers": self.num_threads}
        """
        # user_author_name = input("Channel name: ")
        # user_phrase = input("Enter a phrase: ")
        user_author_name = DEBUG_DATA[0]
        user_phrase = DEBUG_DATA[2]
        url = DEBUG_DATA[1]
        if not url:
            url = input("Enter a url: ")

        videos = self.transcriber.find_videos(yt_url=url)
        print(f"Found a {len(videos)} total!")
        return {"author": user_author_name, "phrase": user_phrase, "videos": videos, "workers": self.num_threads}

    def distribute_work(self, worker_addresses):
        """Send work to nodes across a network
        Args:
            worker_addresses: a comma separated string of addresses of machines
            to distribute work to
        """
        worker_addresses = worker_addresses.split(',')
        
        # Get data to distribute
        payload = self._get_data()

        # split videos among number of workers including itself
        video_splits = balance(payload["videos"], len(worker_addresses) + 1)
        for worker_addr in worker_addresses:
            try:
                video_split = video_splits.pop()
                payload["videos"] = video_split
                res = requests.put(f"http://{worker_addr}:5000/internal/process", json=payload)
                print(res.json())
            except exceptions.ConnectionError:
                print(f"could not reach {worker_addr}")
                video_splits.append(video_split)
        
        # Perform work on the remaining data
        for videos in video_splits:
            print(videos, type(videos))
            payload["videos"] = videos
            self.work(payload)

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
            requests.post(f"http://{self.master_addr}:5000/internal/update", json=data, files={"file": open(f"nodes/matches_{self.transcriber.current_author}.txt", 'rb')})
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

    NOTE: Remainders are distributed starting from the left to right

    Ex:
    a = [1,2,3,4,5,6]
    n = 4
    The length of 'a' is 6 so 6 % 4 = 2.
    balance(a,n) = [[1,2],[3,4],[5],[6]]
    """
    print(f"processing {a}")
    num_items = len(a)
    
    remainder = num_items % n
    # Ignore remainder if the number of lists exceeds the number of items to separate
    # this allows the function to fill most of the lists with at least 1 element
    if(n > num_items):
        remainder = 0

    split = num_items // n

    if not split:
        split = 1

    print(split, remainder, num_items, n)

    # create n sublists
    res = [list() for _ in range(n)]

    # Increment the starting position for every remainder to prevent
    # overlapping of indices
    start_offset = 0
    for i in range(n):
        
        cur_index = split * i + start_offset
        end_index = cur_index + split

        if(remainder > 0):
            end_index += 1
            remainder -= 1
            start_offset += 1
       
        res[i] += a[cur_index: end_index]
      
    return res

# Used to test balance()
if __name__ == "__main__":
    arr = [0, 1, 2, 3, 4, 8, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    a = balance(arr, 20)

    print(a)
