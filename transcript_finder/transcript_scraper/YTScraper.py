from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import re
import time
from datetime import datetime
from .constants import ElementPaths

REGEX_DATE_STR = r'\w{3} \d+, \d{4}'

REGEX_VIDEO_COUNT_STR = r'\d+(.\d+)?'
PAGELOADTIME = 10
WAIT_TIME_BUTTON_LOAD = 10
WAIT_TIME_TRANSCRIPT_LOAD = 12

class YTScraper:
    """Class of methods used to interact with youtube"""
    def convert_video_count_to_int(video_string):
        """Convert videos to an integer
        Ex) 1.4k videos will be converted to 1400
        """
        vids = None
        try:
            vids = int(video_string)
        except ValueError as e:
            vids = re.search(REGEX_VIDEO_COUNT_STR, video_string)
            vid_count = vids.group().split('.')

            if len(vid_count) == 2: 
                thousands, hundreds = vid_count
                vids = (int(thousands) * 1000) + (int(hundreds) * 100)
            else:
                thousands, = vid_count
                vids = int(thousands) * 1000
        return vids

    def get_channel_info(user_entered_owner, driver):
        "Compare name with the official name found on the homepage"
        upload_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'page-header')))

        x = upload_info.find_element(By.TAG_NAME, "yt-content-metadata-view-model")
        x = x.text.split('\n')
        owner = x[0].lower().lstrip('@')
        vids = YTScraper.convert_video_count_to_int(x[-1].split(' ')[0])

      
        print('channel info found', owner, 'videos', vids)
        if user_entered_owner.lower() in owner:
            return owner, vids
        return None, None
    
    def find_videos(url, driver, author):
        """
        Find all Youtube videos present on a webpage
        Args:
            driver: a webdriver tied to a url containing at least 1 youtube video
            url: a string representing the url to open
        Returns:
            a list of urls
        Exception:
            NoSuchElementException: The desired videos to analyze could be in a Youtube playlist; moreover,
                it follows different HTML than if the videos are on the basic Youtube channel page. Thus, this
                exception is used to handle either case
        """
        driver.get(url)
        time.sleep(PAGELOADTIME)
        # determine if playlist exists
        # NOTE: playlist videos use a different ID than homepage video elements
        print("finding videos..")
        videos = []
        try:

            # NOTE: old way to find video element int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0])
            # No issues with it, but this information is included when retrieving the channel name
            _, vid_count = YTScraper.get_channel_info(author, driver)
            
            print(f"rendering {vid_count}")
            YTScraper.scroll_to_bottom(vid_count, driver)

            # NOTE: homepage videos can all be found using ID 'video-title-link' 01/02/24
            videos = driver.find_elements(By.ID, ElementPaths.ID_VIDEO) 

        except Exception as e:
            try:
                # Find all playlist videos
                print("finding videos by playlist method...")
                videos = driver.find_elements(By.ID, ElementPaths.ID_PLAYLIST_VIDEO)
            except Exception as e:
                print(f"error finding videos {str(e)}")
        res = []
        for video in videos:
            video_url = video.get_attribute("href")
            res.append(video_url)

        return res
    
    def get_video_information(driver):
   
        upload_info = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'owner')))

        button_description = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, ElementPaths.XPATH_BUTTON_DESCRIPTION))         
            )
        button_description.click()

        # Requires desc button to be expanded
        upload_date = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'info-container'))).text

        title = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'above-the-fold')))
        title = title.find_element(By.ID, "title").text
        
        date = re.search(REGEX_DATE_STR, upload_date.strip())

        date = datetime.strptime(date.group(),"%b %d, %Y")

        uploader = upload_info.text.split('\n')[0]


        return title, date, uploader


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
    
    def scroll_to_bottom(video_count: int, driver):
        """Scroll to the bottom of a webpage based on the video_count
        Args:
            video_count: an int for the amount of videos that need to be rendered
        NOTE: Youtube initially renders 30 videos.
            Performing bottom scroll renders up to an additional 30 videos(if present).
        """
        print("rendering videos...")

        # Perform one scroll to the bottom of the webpage to handle
        # A bug where prescence of video elements are obscured by Chrome pop-ups
        webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.END).key_up(Keys.CONTROL).key_up(Keys.END).perform()
        time.sleep(3)

        # Scroll to the bottom for every additional 30 videos
        if video_count:
            num_bottom_scroll = ((video_count - 30) // 30)
            if num_bottom_scroll < 0:
                num_bottom_scroll = 1
            print(f"scrolling {num_bottom_scroll} times")
            for _ in range(num_bottom_scroll):   
                webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.END).key_up(Keys.CONTROL).key_up(Keys.END).perform()
                time.sleep(3)
        else:
            print("no video_count: ", video_count, flush=True)

    
    def get_transcript(driver : webdriver.Chrome):
        try:
            # Wait until description element is visible
            button_description = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
            EC.element_to_be_clickable((By.XPATH, ElementPaths.XPATH_BUTTON_DESCRIPTION))         
            )
            button_description.click()
            # Wait until transcript button is visible
            button_transcript = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
                EC.element_to_be_clickable((By.XPATH, ElementPaths.XPATH_BUTTON_TRANSCRIPT))
            )
            button_transcript.click()
            # Wait for transcript content elements to load
            transcript_lines = WebDriverWait(driver, WAIT_TIME_TRANSCRIPT_LOAD).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ElementPaths.CSS_TEXT_TRANSCRIPT))
            )

            script = """
            return Array.from(document.querySelectorAll('segment style-scope ytd-transcript-segment-renderer'))
                        .map(el => el.getAttribute('aria-label'))
                        .join('\\n');
            """
            # One single network round-trip to the Hub
            full_transcript = driver.execute_script(script)
            
            return full_transcript
        except Exception as e:
            return e    
