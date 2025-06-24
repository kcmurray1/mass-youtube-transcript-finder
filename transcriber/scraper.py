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
from transcriber.youtube_element_utils import YtElementUtils


PAGELOADTIME = 10
WAIT_TIME_TRANSCRIPT_LOAD = 20
WAIT_TIME_BUTTON_LOAD = 10

class Scraper:

    def find_videos(yt_url, author, driver : webdriver.Chrome):
        """Extract all videos from a youtube webpage
        
        Args:
            yt_url: A string representing the url to open

        Returns:
            A list of video urls
        """
        # open chromepage at url
        driver.get(yt_url)
        time.sleep(PAGELOADTIME)

        
        # return videos
        return Scraper._find_videos(driver, author)

    
    def _find_videos(driver : webdriver.Chrome, author):
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
        print("finding videos..")
        videos = []
        try:

            # NOTE: old way to find video element int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0])
            # No issues with it, but this information is included when retrieving the channel name
            _, vid_count = YtElementUtils.get_channel_info(author, driver)
            print(f"rendering {vid_count}")
            Scraper._render_videos(vid_count)

            # NOTE: homepage videos can all be found using ID 'video-title-link' 01/02/24
            videos = driver.find_elements(By.ID, Paths.ID_VIDEO) 

        except:
            try:
                # Find all playlist videos
                print("finding videos by playlist method...")
                videos = driver.find_elements(By.ID, Paths.ID_PLAYLIST_VIDEO)
            except Exception as e:
                print(f"error finding videos {e}")
        res = []
        for video in videos:
            video_url = video.get_attribute("href")
            res.append(video_url)

        return res

    def _render_videos(video_count: int):
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

    
    def get_transcript(driver : webdriver.Chrome):
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
            return transcript_lines
        except Exception as e:
            return e    
    

    # Format url to include timestamp, so when it is clicked it jumps to the time
    # Adding timestamps to urls follow the format <url>&t=<hours>h<minutes>m<seconds>s
    # NOTE: unsused
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
    