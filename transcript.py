
import pyautogui
import time
from pynput import mouse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from yt_video import Yt_Video
import threading
import queue
'''
TODO(no priority)
[] make automated testing module
[] see if can include timestamp in link, such that clicking link sends to matched transcript line
    original             https://www.youtube.com/watch?v=u5LJ34hqPF0
    Original_in_playlist https://www.youtube.com/watch?v=Z2Cs0o72yZI&list=RDPT84G0xXDlI&index=2
    Shared link          https://youtu.be/Z2Cs0o72yZI?si=CsyEYxZqkiY2Pf32&t=76
    timestamp line append '&t=<hours>h<minutes>m<seconds>s'
'''
PAGELOADTIME = 5
TRANSCRIPTLOADTIME = 5
file_write_lock = threading.Lock()
progress_lock = threading.Lock()
err_write_lock = threading.Lock()

def valid_author(video_info: str, user_author: str):
    """Verify video is authored by specified author
    Args:
        videoInfo: a str following the format 'by <author> <num views> views Streamed <publish date>
        user_author: a str from the user specifying the name of the youtube channel(author)
    Returns: a bool that describes whether a a video is authored by specified channel
    """
    if video_info is None or user_author is None:
        return False
    # Video is not published by desired author
    if video_info.lower().find(user_author.lower()) == -1:
        return False
    # Video published by desired author
    return True


def get_transcript_matches(driver: webdriver, user_phrase: str):
    """Find lines in a transcript that contain the desired phrase
    Args:
        driver: a webdriver, tied to a Youtube video link, whose transcript will be analyzed
        user_phrase: a str containing a phrase/word to look for in a transcript
    Returns:
        A list containing lines of str containing the desired phrase or
        an empty list if the desired phrase is not found
    Exception:
       TimeoutException: an HTML element did not load in time or does not exist  
    
    FIXME: Currently, the timeout times are hard-coded. May want to replace with expressive constants 
    """
    try:
        # Wait until description element is visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tp-yt-paper-button[@id='expand']"))          
        )
        # Use javascript to click desc button
        driver.execute_script('document.querySelector("#expand").click()')
        # Wait until transcript button is visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ytd-structured-description-content-renderer[@id='structured-description']//ytd-video-description-transcript-section-renderer[@class='style-scope ytd-structured-description-content-renderer']//div[@class='yt-spec-touch-feedback-shape__fill']"))        
        )
        # Use javascript to click transcript button
        driver.execute_script("document.querySelector(\"ytd-structured-description-content-renderer[id='structured-description'] ytd-video-description-transcript-section-renderer[class='style-scope ytd-structured-description-content-renderer'] div[class='yt-spec-touch-feedback-shape__fill']\").click()")
        # Wait for transcript elements to load
        transcript_lines = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='segment style-scope ytd-transcript-segment-renderer']"))
        )
        # Return transcript lines that contain specified phrase
        return [match for line in transcript_lines if (match := line.get_dom_attribute("aria-label")) and user_phrase in match.lower()]
    except TimeoutException:
        return "timeout"

# Format url to include timestamp, so when it is clicked it jumps to the time
# Adding timestamps to urls follow the format <url>&t=<hours>h<minutes>m<seconds>s
def add_timestamp_to_url(url, unformatted_time_info):
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
    

def write_matches(matches: list, user_phrase: str, author: str, url: str):
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
        with err_write_lock:
            print(matches)
            with open("error_log.txt", "a") as err:
                err.write(f"{matches}: {url}\n")
        return

   
    # mutex to ensure only one thread writes to file at a time
    with file_write_lock:
        # write matches to file
        with open(f"matches_{author}.txt", "a") as f:
            # Reduce write operations to files to hopefully improve performance
            # using .join() concats strings in O(n)
            f.write(f"Found {len(matches)} matches containing {user_phrase} URL: {url}\n" + "\n".join(matches) + "\n")

# # Create Yt_Video objects based on video elements scraped on page
# # Playlist videos have different elements than videos displayed on a home channel page
def find_videos(driver: webdriver):
    """
    Find all Youtube videos present on a webpage
    Args:
        driver: a webdriver tied to a url containing at least 1 youtube video
    Returns:
        a list of YT_Video objects 
    Exception:
        NoSuchElementException: The desired videos to analyze could be in a Youtube playlist; moreover,
            it follows different HTML than if the videos are on the basic Youtube channel page. Thus, this
            exception is used to handle either case
    """
    print("Finding Videos...")
    # determine if playlist exists
    # NOTE: playlist videos use a different ID than homepage video elements
    try:
         # Render all of the videos 
        render_videos(int(driver.find_element(By.ID, "videos-count").text.split()[0]))
        videos = driver.find_elements(By.ID, "video-title-link") 
        if videos:
            # NOTE: homepage videos can all be found using ID 'video-title-link' 01/02/24
            # return found videos
            return [Yt_Video(video.get_dom_attribute("aria-label"), video.get_attribute("href")) for video in videos]
    except NoSuchElementException:
        playlist_videos = []
        # Find all playlist videos
        for playlist_video_parent in driver.find_elements(By.ID, "wc-endpoint"):
            # Extract the URL and video title
            playlist_video_url = playlist_video_parent.get_attribute("href")
            playlist_video_title = playlist_video_parent.find_element(By.ID, "video-title").get_dom_attribute("aria-label")
            # Add to list as Yt_Video object
            playlist_videos.append(Yt_Video(playlist_video_title, playlist_video_url))
        # Return videos
        return playlist_videos
    

def render_videos(video_count: int, debug=None):
    """Scroll to the bottom of a webpage based on the video_count
    Args:
        video_count: an int descripting 
    Note: Youtube initially renders 30 videos.
          Performing bottom scroll renders up to an additional 30 videos(if present).
    """
    print("rendering videos...")
    if debug:
        print(f"scrolling {video_count} times")
        for _ in range(video_count):
            pyautogui.hotkey("ctrl", "end")
            time.sleep(3)
        return
    # Scroll to the bottom for every additional 30 videos
    if video_count:
        num_bottom_scroll = (video_count - 30) // 30
        print(f"scrolling {num_bottom_scroll} times")
        for _ in range(num_bottom_scroll):
            pyautogui.hotkey("ctrl", "end")
            time.sleep(3)
        
def dispatch_worker(user_author_name: str, user_phrase: str, video_queue: queue.Queue, id: str):
    """Analyze videos until the given queue is empty
    Args:
        user_author_name: a str of the desired youtube author
        user_phrase: a str describing the desired phrase to find in YT_Videos
        video_queue: thread safe Queue, containing YT_Video objects to be analyzed
        id: a str specifying the 'name' of this worker
    Exception:
        queue.Empty: No more videos need to be processed
    """
    # Open Chromepage dedicated for the worker
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("window-size=1200,1000")
    driver_options.add_argument("mute-audio")
    driver = webdriver.Chrome(options=driver_options)

    while True:
        try:
            # Try to get a video from the queue
            video_to_process = video_queue.get_nowait()
            # validate video author
            if valid_author(video_to_process.get_author(), user_author_name): 
                driver.get(video_to_process.get_url())   
                # Attempt to find a transcript and see if it contains the user's phrase
                write_matches(get_transcript_matches(driver, user_phrase), user_phrase, user_author_name, video_to_process.get_url())
            with progress_lock:
                print(f"Queue size: {video_queue.qsize()}")
        except queue.Empty:
            break
    print(f"{id} is DONE!")
  
def channel_search_multi_thread(threaded_url: str, num_workers=None, video_index=None):
    """Given a URL to a Youtube channel or playlist, find all videos that contain a desired phrase 
    Args:
        threaded_url: a str of Youtube channel or playlist url
        num_workers: int for the number of worker threads to run  
        video_index: tbd 
    """
    if not num_workers or num_workers < 1 or num_workers > 8:
        num_workers = 3
    user_author_name = input("Channel name: ")
    user_phrase = input("Enter a phrase: ")
    # open chromepage at starting url
    driver = webdriver.Chrome()
    driver.get(threaded_url)
    # Resize to prevent element rendering issues
    driver.set_window_size(1200, 1000)
    time.sleep(PAGELOADTIME)
    # get videos and convert into a queue
    videos = find_videos(driver)
    if not videos:
        print("processing single")
        write_matches(get_transcript_matches(driver, user_phrase), user_phrase, user_author_name, threaded_url)
        return
    # Start at a specified position
    # Should mostly be used for debugging purposes since
    # no checks are made
    if video_index:
        location, index = video_index
        if location == "end":
            videos = videos[:index]
        if location == "start":
            videos = videos[index:]
        if location =="debug":
            videos = videos[100: 100 + index]

    # stop main window
    driver.close()
    print(f"total videos: {len(videos)}")
    with open("error_log.txt", "a") as err:
        err.write(f"--{user_author_name}--\n")
    # queue.Queue() is thread-safe
    video_queue = queue.Queue()
    for video in videos:
        video_queue.put(video)

    # assign work
    print(f"assigning {num_workers} workers")
    id = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "tenth"]
    workers = []
    for i in range(num_workers):
        workers.append(threading.Thread(target=dispatch_worker, args=(user_author_name, user_phrase, video_queue, id[i])))
    
    # Start threads
    for worker in workers:
        worker.start()
    # Complete threads
    for worker in workers:
        worker.join()

def debug_test_loop(url, workers, args, num_loops):
    total_time = 0
    for _ in range(num_loops):
        start_time = time.perf_counter
        channel_search_multi_thread(url, workers, args)

        total_time += time.perf_counter - start_time
    return total_time / num_loops

if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=MC7qoiJ5uPc'
    url_long_video = 'https://www.youtube.com/watch?v=SvwjrmKmggs'
    url_no_transcript = 'https://www.youtube.com/watch?v=IdVUOXkA7fk&list=RDwLj-vovaGRs&index=10'
    url_test_homepage = 'https://www.youtube.com/@ScarleYonaguni/streams'
    url_test_homepage_127 = 'https://www.youtube.com/@NerissaRavencroft/streams'
    url_test_homepage_377 = 'https://www.youtube.com/@OuroKronii/streams'
    url_playlist = 'https://www.youtube.com/watch?v=7NxmTYDOPgA&list=PLDWPtsLTdtlDRtFlA61iRpY-ra_71vmAG'
    url_not_youtube = 'https://www.google.com/'
    who = 'https://www.youtube.com/@MoriCalliope/streams'
    url_homepage_27 = 'https://www.youtube.com/@jdh/videos'
    url_test_homepage_655 = 'https://www.youtube.com/@Rosemi_Lovelock/streams'
    url_test_homepage_320 = 'https://www.youtube.com/@LeeandLieVODS/videos'
    url_test_homepage_504 = 'https://www.youtube.com/@EnnaAlouette/streams'
    url_test_homepage_500 = 'https://www.youtube.com/@FujikuraUruka/streams'
    url_kai = 'https://www.youtube.com/@KaiSaikota/streams'
    url_doki = 'https://www.youtube.com/@Dokibird/streams'
    start = time.perf_counter()
    channel_search_multi_thread(url_doki, 6)
    end = time.perf_counter()
    print(f"Elapsed time {end -start:.6f} seconds")
     #res = debug_test_loop(url=url_homepage_27,workers=7, num_loops=5)
   # print(f"Average time processing 22 videos, 5 times: {res} seconds")
