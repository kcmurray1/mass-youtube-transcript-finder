from transcriber.utils.constants.paths import Paths
import pyautogui
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    )
import threading
import queue
from transcriber.yt_video import YtVideo
from transcriber.utils.web_driver_utils import WebdriverUtils
from transcriber.youtube_element_utils import YtElementUtils

PAGELOADTIME = 10
WAIT_TIME_TRANSCRIPT_LOAD = 20
WAIT_TIME_BUTTON_LOAD = 10
LOG_DIR = 'node'

class TranscriptProcessor:
    def __init__(self, id = "default", driver=None):
        self.file_write_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.err_write_lock = threading.Lock()
        self.current_author = None
        self.result_file = None
        self.error_file = None
        self.match_count = 0
        self.error_count = 0
        self.id = id
        self.driver = driver
        # if not driver:
        #     self.driver_settings = WebdriverUtils.get_driver_settings(self.id)


    
    def _get_transcript_matches(self, driver : webdriver, user_phrase: str):
        """Find lines in a transcript that contain the desired phrase
        Args:
            driver: a webdriver, tied to a Youtube video link, whose transcript will be analyzed
            user_phrase: a str containing a phrase/word to look for in a transcript
        Returns:
            A list containing lines of str containing the desired phrase or
            an empty list if the desired phrase is not found
        Exception:
        TimeoutException: an HTML element did not load in time or does not exist  
        """
        try:
            # Wait until description element is visible
            button_description = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
                EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
            )
            button_description.click()
            # Wait until transcript button is visible
            button_transcript = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
                EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_TRANSCRIPT))
            )
            button_transcript.click()
            # Wait for transcript content elements to load
            transcript_lines = WebDriverWait(driver, WAIT_TIME_TRANSCRIPT_LOAD).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, Paths.CSS_TEXT_TRANSCRIPT))
            )
         
            # Return transcript lines that contain specified phrase
            return [match for line in transcript_lines if (match := line.get_dom_attribute("aria-label")) and user_phrase in match.lower()]
        except TimeoutException:
            return "timeout"

    # Format url to include timestamp, so when it is clicked it jumps to the time
    # Adding timestamps to urls follow the format <url>&t=<hours>h<minutes>m<seconds>s
    # NOTE: unsused
    def add_timestamp_to_url(self, url, unformatted_time_info):
        if not unformatted_time_info:
            return
        # All unformatted time_info follows the format(oxymoronic):
        # <num_hours> hours, <num_minutes> minutes, <num_seconds> seconds <text>
        # Thus, split by spaces and filter hours, minutes, and seconds
        words = unformatted_time_info.split()
        # Amass a list to perform linear time join at end
        timestampUrl = [url, '&t=']
        # Iterate from the left of the information to glean timestamp values
        for index, word in enumerate(words):
            if 'hour' in word:
                timestampUrl.append(''.join([words[index - 1], "h"]))
            if 'minute' in word:
                timestampUrl.append(''.join([words[index - 1], "m"]))
            if 'second' in word:
                timestampUrl.append(''.join([words[index - 1], "s"]))
                break
        
        # Return url containing timestamp
        return ''.join(timestampUrl)
    

    def _write_matches(self, matches: list, user_phrase: str, author: str, url: str):
        """Write matches to a file, named as the author, in a formatted manner
        
        Ex:
        If the author is 'apple', then the method will write to 'matches_apple.txt'
        If n is the length of the list of matches, then the method will output to the file:
    
            Found n matches containing hello URL: <url>
            <timestamp_1> <1st sentence containing phrase>
            <timestamp_2> <2nd sentence containing phrase>
            ...
            <timestamp_n> <nth sentence containing phrase>

        Note: This method also write errors to a file called 'error_log.txt' as:
            timeout: <url>
        """
        if not matches:
            return
        
        # Write to error log when matches is a string
        if isinstance(matches, str):
            with self.err_write_lock:
                print(matches)
                with open(self.error_file, "a") as err:
                    self.error_count += 1
                    err.write(f"{matches}: {url}\n")
            return

    
        # mutex to ensure only one thread writes to file at a time
        with self.file_write_lock:
            # write matches to file
            with open(self.result_file, "a") as f:
                self.match_count += len(matches)
                # Reduce write operations to files to hopefully improve performance
                # using .join() concats strings in O(n)
                f.write(f"Found {len(matches)} matches containing {user_phrase} URL: {url}\n" + "\n".join(matches) + "\n")

    def _find_videos(self, driver : webdriver.Chrome):
        """
        Helper to Find all Youtube videos present on a webpage
        Args:
            driver: a webdriver tied to a url containing at least 1 youtube video
        Returns:
            a list of urls
        Exception:
            NoSuchElementException: The desired videos to analyze could be in a Youtube playlist; moreover,
                it follows different HTML than if the videos are on the basic Youtube channel page. Thus, this
                exception is used to handle either case
        """
        # determine if playlist exists
        # NOTE: playlist videos use a different ID than homepage video elements
        videos = []
        try:

            # NOTE: old way to find video element int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0])
            # No issues with it, but this information is included when retrieving the channel name
            _, vid_count = YtElementUtils.get_channel_info(self.current_author, driver)
            print(f"rendering {vid_count}")
            self._render_videos(vid_count)

            # NOTE: homepage videos can all be found using ID 'video-title-link' 01/02/24
            videos = driver.find_elements(By.ID, Paths.ID_VIDEO) 

        except NoSuchElementException:
            # Find all playlist videos
            videos = driver.find_elements(By.ID, Paths.ID_PLAYLIST_VIDEO)
        except Exception as e:
            print(f"error finding videos {e}")
        res = []
        for video in videos:
            video_url = video.get_attribute("href")

            res.append(video_url)
        return res
    
    def find_videos(self, yt_url, driver=None):
        """Extract all videos from a youtube webpage
        
        Args:
            yt_url: A string representing the url to open

        Returns:
            A list of video urls
        """
        # open chromepage at starting url
        if not driver:
            # driver = webdriver.Chrome(options=self.driver_settings)
            driver = webdriver.Chrome()
        driver.get(yt_url)
        time.sleep(PAGELOADTIME)

        
        # return videos
        videos = self._find_videos(driver=driver)

        if not driver:
            driver.close()
        return videos

       
    def _render_videos(self, video_count: int):
        """Scroll to the bottom of a webpage based on the video_count
        Args:
            video_count: an int descripting 
        NOTE: Youtube initially renders 30 videos.
            Performing bottom scroll renders up to an additional 30 videos(if present).
        """
        print("rendering videos...")

        # Perform one scroll to the bottom of the webpage to handle
        # A bug where prescence of video elements are obscured by Chrome pop-ups
        pyautogui.hotkey("ctrl", "end")
        time.sleep(3)

        # Scroll to the bottom for every additional 30 videos
        if video_count:
            num_bottom_scroll = ((video_count - 30) // 30)
            print(f"scrolling {num_bottom_scroll} times")
            for _ in range(num_bottom_scroll):
                pyautogui.hotkey("ctrl", "end")
                time.sleep(3)
        else:
            print("no video_count: ", video_count, flush=True)
        
    def _dispatch_worker(self, user_author_name: str, user_phrase: str, video_queue: queue.Queue, id: str):
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
        
        worker_driver = webdriver.Chrome()

        while True:
            try:
                # Try to get a video from the queue
                video_url = video_queue.get_nowait()
             
                    # Attempt to find a transcript and see if it contains the user's phrase
                worker_driver.get(video_url)  

                self._write_matches(self._get_transcript_matches(worker_driver, user_phrase), user_phrase, user_author_name, video_url)
              
                with self.progress_lock:
                    print(f"Queue size: {video_queue.qsize()}", end='\r')
            # Restart work if an uncaught exception is thrown
            except (Exception, queue.Empty) as e:
                if isinstance(e, queue.Empty):
                    break
                continue

        print(f"{id} is DONE!")

        worker_driver.quit()

  
    
    def channel_search(self, num_workers=None, url=None, author=None, phrase=None):
        """Given a list of videos, find all videos of a specified author containing a desired phrase 
        Args:
            videos: a list of Yt_video objects to operate on
            num_workers: int for the number of worker threads to run
            author: a str for the name of the youtube channel
            phrase: a str for the phrase to look for  
        """
        if not num_workers or num_workers < 1 or num_workers > 8:
            num_workers = 3
        self.current_author = author

        videos = self.find_videos(url)
        # Update class attributes
 
        self.result_file = f"{LOG_DIR}/matches_{author}.txt"
        self.error_file = f"{LOG_DIR}/error_log.txt"
        print(f"total videos: {len(videos)}")
        with open(self.error_file, "a") as err:
            err.write(f"--{author}--\n")
        # NOTE: queue.Queue() is thread-safe
        video_queue = queue.Queue()
        for video in videos:
            video_queue.put(video)

        # assign work to threads
        print(f"assigning {num_workers} workers")
        id = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "tenth"]
        workers = []
        for i in range(num_workers):
            workers.append(threading.Thread(target=self._dispatch_worker, args=(author, phrase, video_queue, id[i])))
        
        # Start threads
        for worker in workers:
            worker.start()
        # Complete threads
        for worker in workers:
            worker.join()
   
      
       