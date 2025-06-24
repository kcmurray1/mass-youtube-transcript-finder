from selenium import webdriver
import queue
from transcriber.scraper import Scraper
from transcriber.logger import Logger

class ScraperWorker:
    def __init__(self, id, logger : Logger):
        self.id = id
        self.driver = webdriver.Chrome()
        self.logger = logger

    def work(self, channel_name: str, user_phrase: str, video_queue: queue.Queue, id: str):
        """Analyze videos until the given queue is empty
        Args:
            user_author_name: a str of the desired youtube author
            user_phrase: a str describing the desired phrase to find in YTVideos
            video_queue: thread safe Queue, containing YTVideo objects to be analyzed
            id: a str specifying the 'name' of this worker
        Exception:
            queue.Empty: No more videos need to be processed
        """
        # Open Chromepage dedicated for the worker
        # driver_options = webdriver.ChromeOptions()
        # driver_options.add_argument("window-size=1200,1000")
        # driver_options.add_argument("mute-audio")
        # worker_driver = webdriver.Chrome(options=self.driver_settings)
        while True:
            try:
                # Try to get a video from the queue
                video_url = video_queue.get_nowait()
             
                    # Attempt to find a transcript and see if it contains the user's phrase
                self.driver.get(video_url)  

                transcript = Scraper.get_transcript(self.driver, user_phrase), user_phrase, user_author_name, video_url

                if isinstance(transcript, Exception):
                    self.logger.log_err(video_url)
                else:
                    self.logger.log()

            # Restart work if an uncaught exception is thrown
            # or stop if the queue is empty
            except (Exception, queue.Empty) as e:
                if isinstance(e, queue.Empty):
                    break
                continue

        # close driver
        self.driver.quit()

    def log_db(self, db):
        pass