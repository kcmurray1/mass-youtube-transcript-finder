
import pyautogui
import time
from pynput import mouse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from yt_video import Yt_Video
import threading
import queue
# TODO(no priority)
'''
[x] automatically determine whether link is a homepage or contains a playlist
[] make automated testing module
[x] debuf_render_videos by finding total videos in channel
[x] change find_phrase_in_transcript to send formatted output to file
[] see if can include timestamp in link, such that clicking link sends to matched transcript line
    original             https://www.youtube.com/watch?v=u5LJ34hqPF0
    Original_in_playlist https://www.youtube.com/watch?v=Z2Cs0o72yZI&list=RDPT84G0xXDlI&index=2
    Shared link          https://youtu.be/Z2Cs0o72yZI?si=CsyEYxZqkiY2Pf32&t=76
[x] multirthread
[]  
'''
PAGELOADTIME = 5
TRANSCRIPTLOADTIME = 5
NEXTVIDEOLOADTIME = 5
file_write_lock = threading.Lock()
progress_lock = threading.Lock()

# verify video is authored by specified author
def valid_author(videoInfo, user_author):
    # invalid input
    if videoInfo is None or user_author is None:
        return False
    #print("VALIDATING:", videoInfo)
    # Video is not published by desired author
    if videoInfo.lower().find(user_author) == -1:
        return False
    # Video published by desired author
    return True

# return a transcript as a list of strings
# return empty list if transcript could not be retrieved
def get_transcript(driver):
    #print("Retrieving transcript..")
    try:
        # find description expander to reveal transcript button
        button = driver.find_element(By.XPATH, "//tp-yt-paper-button[@id='expand']")
        button.click()
        time.sleep(3)
        # Check if transcript button exists
        transcript_button = driver.find_element(By.XPATH, "//ytd-structured-description-content-renderer[@id='structured-description']//ytd-video-description-transcript-section-renderer[@class='style-scope ytd-structured-description-content-renderer']//div[@class='yt-spec-touch-feedback-shape__fill']")
        transcript_button.click()
        time.sleep(TRANSCRIPTLOADTIME)
        # Return transcript as list of strings
        return [x.get_dom_attribute("aria-label") for x in driver.find_elements(By.CSS_SELECTOR, "div[class='segment style-scope ytd-transcript-segment-renderer']")]
    # No transcript element exists
    except NoSuchElementException:
        print("no transcript!")
        return "No transcript"
    # FIXME: perform operation again
    except ElementClickInterceptedException:
        print("intercepted!")
        return "Intercepted"

# Find a user_phrase in a given transcript
def find_phrase_in_transcript(transcript, user_phrase, author, url, debug=False):
    if not isinstance(transcript, list):
        with open("error_log.txt", "a") as err:
            err.write(f"{transcript}: {url}\n")
    matches = []
    # Find user_phrase in transcript
    for line in transcript:
        if(user_phrase in line.lower()):
            matches.append(line)
    # Write to file with format
    # Found <num_matches> containing <user_phrase> URL: <url>
    # <match 1>\n
    # <match 2>\n
    # ...
    if matches:
        # mutex to ensure only one thread writes to file at a time
        with file_write_lock:
            # write matches to file
            with open(f"matches_{author}.txt", "a") as f:
                # Reduce write operations to files to hopefully improve performance
                # using .join() concats strings in O(n)
                f.write(f"Found {len(matches)} matches containing {user_phrase} URL: {url}\n" + "\n".join(matches) + "\n")
    

# # Create Yt_Video objects based on video elements scraped on page
# # Playlist videos have different elements than videos displayed on a home channel page
def find_videos(driver):
    print("Finding Videos...")
    # determine if playlist exists
    # NOTE: playlist videos use a different ID than homepage video elements
    try:
         # Render all of the videos 
        render_videos(int(driver.find_element(By.ID, "videos-count").text.split()[0]))
        #render_videos(5, True)
        videos = driver.find_elements(By.ID, "video-title-link")
        print(len(videos))
        if videos:
            # NOTE: homepage videos can all be found using ID 'video-title-link' 01/02/24
            # return found videos
            return [Yt_Video(video.get_dom_attribute("aria-label"), video.get_attribute("href")) for video in videos]
    except NoSuchElementException:
        #print("Could not find vdeos using: video-title-link")
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
    
# scroll to the bottom of a webpage for specified amount of times
def render_videos(video_count, debug=None):
    print("rendering videos...")
    # Youtube initially renders 30 videos
    # performing bottom scroll renders an additional 30 videos(if present)
    if debug:
        print(f"scrolling {video_count} times")
        for _ in range(video_count):
            pyautogui.hotkey("ctrl", "end")
            time.sleep(3)
        return
    if video_count:
        num_bottom_scroll = (video_count - 30) // 30
        print(f"scrolling {num_bottom_scroll} times")
        for _ in range(num_bottom_scroll):
            pyautogui.hotkey("ctrl", "end")
            time.sleep(3)
        
# Workers receive work via a Queue
def dispatch_worker(start_url, user_author_name, user_phrase, video_queue, id):
    # open chromepage at starting url
    driver = webdriver.Chrome()
    driver.get(start_url)
    # Resize to prevent element rendering issues
    driver.set_window_size(1200, 1000)
    time.sleep(PAGELOADTIME)

    # Get a video to process from the queue
    while True:
        try:
            # Try to get a video from the queue
            # raises queue.Empty if queue is empty
            video_to_process = video_queue.get_nowait()
            # validate video author
            if valid_author(video_to_process.get_author(), user_author_name): 
                driver.get(video_to_process.get_url())   
                # Wait for the new video to load
                time.sleep(NEXTVIDEOLOADTIME)
                # Attempt to find a transcript and see if it contains the user's phrase
                find_phrase_in_transcript(get_transcript(driver), user_phrase, user_author_name, video_to_process.get_url())
            with progress_lock:
                print(f"Queue size: {video_queue.qsize()}")
        except queue.Empty:
            break
    print(f"{id} is DONE!")
  
def channel_search_multi_thread(threaded_url, num_workers=None, video_index=None):
    if not num_workers or num_workers < 1 or num_workers > 8:
        num_workers = 2
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

    # Start at a specified position
    # Should mostly be used for debugging purposes since
    # no checks are made
    if video_index:
        #videos = videos[video_index:]
        videos = videos[:video_index]
    # stop main window
    driver.close()
    print(f"total videos: {len(videos)}")
    
    # queue.Queue() is thread-safe
    video_queue = queue.Queue()
    for video in videos:
        video_queue.put(video)

    # assign work
    print(f"assigning {num_workers} workers")
    id = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "tenth"]
    workers = []
    for i in range(num_workers):
        workers.append(threading.Thread(target=dispatch_worker, args=(threaded_url, user_author_name, user_phrase, video_queue, id[i])))
    # Start threads
    for worker in workers:
        worker.start()
    # Complete threads
    for worker in workers:
        worker.join()


def extract_text(url):
    # start driver
    # open chromepage at starting url
    driver = webdriver.Chrome()
    driver.get(url)
    # Resize to prevent element rendering issues
    driver.set_window_size(1200, 1000)
    time.sleep(PAGELOADTIME)

    #NOTE: Uncomment to test current method to find and search transcripts
    #find_phrase_in_transcript(get_transcript(driver), "hello", "debug", url)
    button = driver.find_element(By.XPATH, "//tp-yt-paper-button[@id='expand']")
    button.click()
    time.sleep(3)
    # Check if transcript button exists
    transcript_button = driver.find_element(By.XPATH, "//ytd-structured-description-content-renderer[@id='structured-description']//ytd-video-description-transcript-section-renderer[@class='style-scope ytd-structured-description-content-renderer']//div[@class='yt-spec-touch-feedback-shape__fill']")
    transcript_button.click()
    time.sleep(TRANSCRIPTLOADTIME)
    # Get transcript element
    x = driver.find_element(By.TAG_NAME, "ytd-transcript-renderer")
    # Get text
    print(len(x.text), "hello" in x.text)

    driver.close()

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
    start = time.perf_counter()
    channel_search_multi_thread(who, 7, 400)

    #extract_text(url)
    end = time.perf_counter()
    print(f"Elapsed time {end -start:.6f} seconds")