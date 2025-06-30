from selenium import webdriver
import queue
import threading
from transcriber.scraper import Scraper
from transcriber.scraperworker import ScraperWorker
from transcriber.logger import Logger


class ScraperThreaded:
    def get_transcripts(videos, author, log : Logger, transcript_op=None, num_workers=None):
        """Given a list of videos, find all videos of a specified author containing a desired phrase 
        Args:
            url: a youtube url for a channel homepage or playlist
            num_workers: int for the number of worker threads to run  
        """
        if not num_workers or num_workers < 1 or num_workers > 8:
            num_workers = 3

        print(f"total videos: {len(videos)}")

        # NOTE: queue.Queue() is thread-safe
        video_queue = queue.Queue()
        for video in videos:
            video_queue.put(video)

        # assign work to threads
        print(f"assigning {num_workers} workers")

        workers = []
        for i in range(num_workers):
            new_worker = ScraperWorker(id=i, logger=log)
            workers.append(threading.Thread(target=new_worker.get_transcript_v2, args=(video_queue, ScraperWorker.basic_video_handler, transcript_op)))
        
        # Start threads
        for worker in workers:
            worker.start()
        # Complete threads
        for worker in workers:
            worker.join()