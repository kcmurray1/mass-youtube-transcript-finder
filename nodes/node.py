import requests
from transcriber.transcript import TranscriptProcessor
from requests import exceptions

class Node:
    def __init__(self):
        self.is_master = False
        self.master_addr = None
        self.transcriber = TranscriptProcessor()



    def distribute_work(self, worker_addresses):
        """Send work to nodes across a network"""
        self.is_master = True
        worker_addresses = worker_addresses.split(',')

        x = [i for i in range(200)]
        data = {"data": x}

        for worker_addr in worker_addresses:
            try:
                res = requests.put(f"http://{worker_addr}/process", json=data)
                print(res.json())
            except exceptions.ConnectionError:
                print(f"could not reach {worker_addr}")

    def work(self, url, num_threads=None, author=None, phrase=None):
        self.transcriber.channel_search_multi_thread(url, num_threads, author, phrase)
        #self.send_results(data)
    
    def send_results(self, data):
        res = requests.put(f"http://localhost:5000/update", json=data)


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
      

    print(res)


if __name__ == "__main__":
    arr = [0,1,3]
    balance(arr, 5)