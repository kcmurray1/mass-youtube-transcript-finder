from selenium import webdriver
import queue
from transcriber.scraper import Scraper
from transcriber.logger import Logger

class ScraperWorker:
    def __init__(self, id, logger : Logger):
        self.id = id
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("mute-audio")
        self.driver = webdriver.Chrome(options=driver_options)
        self.logger = logger

    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])

    def get_transcript(self, video_queue : queue.Queue, transcript_op=default_transcript):
        """Analyze videos until the given queue is empty
        Args:
            video_queue: thread safe Queue, containing video urls to process

        Exception:
            queue.Empty: No more videos need to be processed
        """
        while True:
            try:
                # Try to get a video from the queue
                video_url = video_queue.get_nowait()
             
                    # Attempt to find a transcript and see if it contains the user's phrase
                self.driver.get(video_url)  

                transcript = Scraper.get_transcript(self.driver)


                if isinstance(transcript, Exception):
                    self.logger.log_err(video_url)
                else:
                    self.logger.log(transcript_op(transcript))
                

            # Restart work if an uncaught exception is thrown
            # or stop if the queue is empty
            except (Exception, queue.Empty) as e:
                if isinstance(e, queue.Empty):
                    break
                continue

        # close driver
        self.driver.quit()
