
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
# TODO(no priority)
'''
[x] automatically determine whether link is a homepage or contains a playlist
[] make automated testing module
[x] debuf_render_videos by finding total videos in channel
[] change find_phrase_in_transcript to send formatted output to file
[] see if can include timestamp in link, such that clicking link sends to matched transcript line
    original             https://www.youtube.com/watch?v=u5LJ34hqPF0
    Original_in_playlist https://www.youtube.com/watch?v=Z2Cs0o72yZI&list=RDPT84G0xXDlI&index=2
    Shared link          https://youtu.be/Z2Cs0o72yZI?si=CsyEYxZqkiY2Pf32&t=76
[] multirthread
[]  
'''
PAGELOADTIME = 5
TRANSCRIPTLOADTIME = 5
NEXTVIDEOLOADTIME = 5
file_write_lock = threading.Lock()

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
        # Return transcript
        return [x.get_dom_attribute("aria-label") for x in driver.find_elements(By.CSS_SELECTOR, "div[class='segment style-scope ytd-transcript-segment-renderer']")]
    # No transcript element exists
    except NoSuchElementException:
        print("no transcript!")
    # FIXME: perform operation again
    except ElementClickInterceptedException:
        print("intercepted!")
    return []

# Find a user_phrase in a given transcript
def find_phrase_in_transcript(transcript, user_phrase, author, url, debug=False):
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
                f.write(f"Found {len(matches)} matches containing {user_phrase} URL: {url}\n")
                f.writelines(f"{line}\n" for line in matches)
    

# # Create Yt_Video objects based on video elements scraped on page
# # Playlist videos have different elements than videos displayed on a home channel page
def find_videos(driver):
    print("Finding Videos...")
    # determine if playlist exists
    # NOTE: playlist videos use a different ID than homepage video elements
    try:
         # Render all of the videos 
        render_videos(int(driver.find_element(By.ID, "videos-count").text.split()[0]))
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
def render_videos(video_count):
    print("rendering videos...")
    # Youtube initially renders 30 videos
    # performing bottom scroll renders an additional 30 videos(if present)
    if video_count:
        num_bottom_scroll = (video_count - 30) // 30
        print(f"scrolling {num_bottom_scroll} times")
        for _ in range(num_bottom_scroll):
            pyautogui.hotkey("ctrl", "end")
            time.sleep(3)
        
# find the transcript generated by video url
def channel_search(start_url, user_author_name=None, user_phrase=None, partition=None):
    if user_author_name is None and user_phrase is None: 
        user_author_name = input("Channel name: ")
        user_phrase = input("Enter a phrase: ")
    # open chromepage at starting url
    driver = webdriver.Chrome()
    driver.get(start_url)
    # Resize to prevent element rendering issues
    driver.set_window_size(1200, 1000)
    time.sleep(PAGELOADTIME)
    videos = find_videos(driver)

    # split
    mid = len(videos) // 2
    quart = mid // 2
    if partition == "first":
        videos = videos[:quart]
    if partition == "second":
        videos = videos[quart: 2 * quart]
    if partition == "third":
        videos = videos[2 * quart: 3 * quart]
    if partition == "fourth":
        videos = videos[3 * quart: 4 * quart + 1]
    num_videos = len(videos)
    for index, video in enumerate(videos):
        print(f"{partition} processing video ({index + 1}/{num_videos})")
        # if videos.index(video) < 68:
        #    continue
        if valid_author(video.get_title(), user_author_name): 
            driver.get(video.get_url())
                # Resize to prevent element rendering issues
       
            # Wait for the new video to load
            time.sleep(NEXTVIDEOLOADTIME)
            #print("moving to next video")
            # Attempt to find a transcript and see if it contains the user's phrase
            find_phrase_in_transcript(get_transcript(driver), user_phrase, user_author_name, video.get_url())
    # Close the page
    driver.close()

    

def channel_search_multi_thread(threaded_url):
    # user_author_name = input("Channel name: ")
    # user_phrase = input("Enter a phrase: ")
    # find all videos
    make_workers(4, threaded_url)
    # split into fourths
    # t1 = threading.Thread(target=channel_search, args=(threaded_url, user_author_name, user_phrase, "first"))
    # t2 = threading.Thread(target=channel_search, args=(threaded_url, user_author_name, user_phrase, "second"))
    # t3 = threading.Thread(target=channel_search, args=(threaded_url, user_author_name, user_phrase, "third"))
    # t4 = threading.Thread(target=channel_search, args=(threaded_url, user_author_name, user_phrase, "fourth"))

    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()

    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()

def make_workers(num_workers, threaded_url):
    id = ["first", "second", "third", "fourth"]
    user_author_name = input("Channel name: ")
    user_phrase = input("Enter a phrase: ")
    workers = []

    # initialize workers
    for i in range(num_workers):
        workers.append(threading.Thread(target=channel_search, args=(threaded_url, user_author_name, user_phrase, id[i])))
    
    # Start workers
    for worker in workers:
        worker.start()
    
    # Join workers
    for worker in workers:
        worker.join()


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
    channel_search_multi_thread('https://www.youtube.com/@jdh/videos')

    #channel_search(url_homepage_27)