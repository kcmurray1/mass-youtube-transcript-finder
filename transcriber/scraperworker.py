from selenium import webdriver
import queue
from transcriber.scraper import Scraper
from transcriber.logger import Logger, DBLogger

class ScraperWorker:
    def __init__(self, id, logger : Logger):
        self.id = id
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("mute-audio")
        self.driver = webdriver.Chrome(options=driver_options)
        self.logger = logger

    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])
    
    def basic_video_handler(driver, video_url, logger : Logger, transcript_op):
        driver.get(video_url)  
        # Get transcript
        transcript = Scraper.get_transcript(driver)

        if isinstance(transcript, Exception):
            logger.log_err([video_url, '\n'])
        else:
            if transcript is not None and transcript != []:
                logger.log([video_url, '\n' ,transcript_op(transcript), '\n'])

    def db_video_handler(diver, video_url, logger : DBLogger, transcript_op):
        # get video information

        # get channel id/insert channel if does not exist
        
        # insert video with channel id

        # insert transcript
        pass

            
    def get_transcript_v2(self, video_queue : queue.Queue, video_handler, transcript_op=default_transcript):
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
             
                # Perform operation on video_url and log it to desired source
                video_handler(self.driver, video_url, self.logger, transcript_op)

            # Restart work if an uncaught exception is thrown
            # or stop if the queue is empty
            except (Exception, queue.Empty) as e:
                if isinstance(e, queue.Empty):
                    break
                continue

        # close driver
        self.driver.quit()
