from transcriber.utils.constants.paths import Paths
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
from transcriber.static_page import StaticPage
from transcriber.dynamic_page import DynamicPage
REGEX_DATE_STR = r'\w{3} \d+, \d{4}'

PAGELOADTIME = 10

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
            _, vid_count = StaticPage.get_channel_info(author, driver)
            print(f"rendering {vid_count}")
            DynamicPage.scroll_to_bottom(vid_count)

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
    
    def get_video_information(driver : webdriver):
   
        upload_info = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'owner')))


        url = upload_info.find_element(By.TAG_NAME, "a").get_attribute("href")

        button_description = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
            )
        button_description.click()

        # Requires desc button to be expanded
        upload_date = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'info-container'))).text

        title = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'above-the-fold')))
        title = title.find_element(By.ID, "title").text
        


        
        date = re.search(REGEX_DATE_STR, upload_date.strip())

        date = datetime.strptime(date.group(),"%b %d, %Y")

        uploader = upload_info.text.split('\n')[0]

        # print(url, title, "//", date.date(), uploader)

        return url, title, date, uploader


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
    