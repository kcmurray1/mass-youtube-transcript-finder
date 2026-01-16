from selenium import webdriver
import queue
from mysql.connector.errors import PoolError
from .YTScraper import YTScraper
class ScraperWorker:
    def __init__(self, id, selenium_addr="127.0.0.1"):
        self.id = id
        self.target_addr = selenium_addr
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("mute-audio")
        driver_options.add_argument("--windows-size=1920,1080")
        driver_options.add_argument("--headless=new")    
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        driver_options.add_argument(f"user-agent={ua}")
        driver_options.add_argument("--disable-blink-features=AutomationControlled")
        driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver_options.add_experimental_option('useAutomationExtension', False)
        driver_options.add_argument("--lang=en-US")
        driver_options.add_argument("--headless=new")
        self.driver = webdriver.Remote(command_executor=f"http://{selenium_addr}:4444", options=driver_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
        })
   

    def get_transcript_v2(self, video_queue : queue.Queue, video_handler, transcript_op):
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
                video_handler(self.driver, video_url, transcript_op)
                
            # stop if the queue is empty and skip over videos that with Exceptions thrown
            except (Exception, queue.Empty) as e:
                
                if isinstance(e, queue.Empty):
                    print("queue empty!")
                    self.driver.quit()
                    break
                print(f"Worker Video error {video_url}:{str(e)}")
                continue

   